from src import helpers
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
import re
from math import isclose  # For float comparisons
from src.text_engines import google, qwant

ENGINES = [
    google,
    qwant,
]
ratelimited_timestamps = {}


def handleUserInfoQueries(query: str) -> str | None:
    if any(query.lower().find(valid_ip_prompt) != -1 for valid_ip_prompt in VALID_IP_PROMPTS):
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[-1].strip()
        return request.remote_addr or "unknown"
    elif any(query.lower().find(valid_ua_prompt) != -1 for valid_ua_prompt in VALID_UA_PROMPTS):
        return request.headers.get("User-Agent") or "unknown"
    return None


def textResults(query: str) -> Response:
    global ratelimited_engines
    # get user language settings
    settings = helpers.Settings()

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    with open(f'static/lang/{settings.ux_lang}.json', 'r') as file:
        lang_data = helpers.format_araa_name(json.load(file))

    # used to measure time spent
    start_time = time.time()

    api = args.get("api", "false")
    search_type = args.get("t", "text")
    p = args.get("p", 0)

    results = None
    ratelimited = True # Used to determine if complete engine failure is due to a bug or due to
                       # the server getting completely ratelimited from every supported engine.

    engine_list = []
    for engine in ENGINES:
        if engine.NAME == settings.engine:
            # Put prefered engine at the top of the list
            engine_list = [engine] + engine_list
        else:
            engine_list.append(engine)


    try:
        for ENGINE in engine_list:
            if (t := ratelimited_timestamps.get(ENGINE.__name__)) is not None and t + ENGINE_RATELIMIT_COOLDOWN_MINUTES * 60 >= time.time():
                # Current engine is ratelimited. Skip it.
                continue
            results = ENGINE.search(query, p, search_type, settings)
            if results.code == 429:
                t = time.time()
                print(f"Text engine {results.engine} was just ratelimited (time={t})")
                ratelimited_timestamps[ENGINE.__name__] = t
            else: # Server *likely* isn't ratelimited.
                ratelimited = False
            if results.ok:
                break
            print(f"WARN: Text engine {results.engine} failed with code {results.code}.")
            if results.code == 429:
                print("NOTE: this engine just got ratelimited.")
            else:
                print(f"Response: {results}")
            results = None
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if results is None:
        if ratelimited: # Server is completely ratelimited :(.
            return jsonify({"instance_rate_limited": "The instance you are using is rate limited for every supported engine. Try again later."}), 429
        else: # *Likely* not ratelimited. Something probably went wrong.
            return jsonify({"error": "Complete engine failure. If this occurs multiple times, then " \
                "this is *likely* an extremely unfortanute bug. Some additional " \
                "information is provided with this error.", "query": query, "type": search_type}), 500

    elapsed_time = time.time() - start_time

    # gets users ip or user agent
    info = handleUserInfoQueries(query)
    calc = ""
    exported_math_expression = ""
    # calculator (TODO: Maybe remove expression parsing. It behaves in odd ways, and in general people who need a calculator can just search calculator)
    if info == None:
        info = ""
        math_expression = re.search(r'(\d+(\.\d+)?)\s*([\+\-\*/x])\s*(\d+(\.\d+)?)', query)
        if math_expression:
            exported_math_expression = math_expression.group(0)
            num1 = float(math_expression.group(1))
            operator = math_expression.group(3)
            num2 = float(math_expression.group(4))

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == 'x':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if not isclose(num2, 0) else "Err; cannot divide by 0."

            try:
                result = float(result)
                if result.is_integer():
                    result = int(result)
            except:
                pass

            calc = result
        elif "calculator" in query.lower():
            calc = "0"
        else:
            calc = ""

    if api == "true" and API_ENABLED == True:
        # return the results as a JSON response
        return jsonify(results.asDICT())
    else:
        check = "" if results.correction is None else results.correction
        snip = "" if results.featured is None else results.featured

        return render_template("results.html",
                               engine=results.engine,
                               results=results.results, sublink=results.top_result_sublinks, p=p, title=f"{query} - {ARAA_NAME}",
                               q=f"{query}", fetched=f"{elapsed_time:.2f}",
                               snip=f"{snip}",
                               user_info=f"{info}", calc=f"{calc}", check=check, current_url=request.url,
                               type=search_type, repo_url=REPO, donate_url=DONATE, commit=helpers.latest_commit(),
                               exported_math_expression=exported_math_expression, API_ENABLED=API_ENABLED,
                               TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
                               settings=settings, wiki=results.wiki, araa_name=ARAA_NAME,
                               before=args.get("before", ""), after=args.get("after", "")
                               )
