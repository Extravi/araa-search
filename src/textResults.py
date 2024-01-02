from src import helpers
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
import re
from math import isclose  # For float comparisons
from src.textEngines import google, qwant


def textResults(query) -> Response:
    # get user language settings
    settings = helpers.Settings()

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    try:
        results = google.search(settings)
    except Exception:
        results = qwant.search(settings)

    # gets users ip or user agent
    info = ""
    calc = ""
    if any(query.lower().find(valid_ip_prompt) != -1 for valid_ip_prompt in VALID_IP_PROMPTS):
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            ip = xff.split(",")[-1].strip()
        else:
            ip = request.remote_addr or "unknown"
        info = ip
    elif any(query.lower().find(valid_ua_prompt) != -1 for valid_ua_prompt in VALID_UA_PROMPTS):
        user_agent = request.headers.get("User-Agent") or "unknown"
        info = user_agent
    # calculator
    else:
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

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    current_url = request.url

    if "exported_math_expression" not in locals():
        exported_math_expression = ""

    api = args.get("api", "false")
    if api == "true" and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        type = args.get("t", "text")
        return render_template("results.html",
                               args=args,
                               q=query, p=args.get("p", 0),
                               title=f"{query} - Araa",
                               fetched=f"{elapsed_time:.2f}",
                               user_info=info, calc=calc, current_url=current_url,
                               type=type, repo_url=REPO, donate_url=DONATE, commit=helpers.latest_commit(),
                               exported_math_expression=exported_math_expression, API_ENABLED=API_ENABLED,
                               TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
                               settings=settings,
                               results=results
                               )
