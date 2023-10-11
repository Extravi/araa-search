from src.helpers import makeHTMLRequest, latest_commit
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
import re
from math import isclose # For float comparisons


def textResults(query) -> Response:
    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")
    search_type = request.args.get("t", "text")
    p = request.args.get("p", 0)
    lang = request.cookies.get('lang', '')
    safe = request.cookies.get('safe', 'active')
    domain = request.cookies.get('domain', 'google.com/search?gl=us')
    javascript = request.cookies.get('javascript', 'enabled')

    try:
        # search query
        if search_type == "reddit":
            site_restriction = "site:reddit.com"
            query_for_request = f"{query} {site_restriction}"
            soup = makeHTMLRequest(f"https://www.{domain}&q={quote(query_for_request)}&start={p}&lr={lang}")
        elif search_type == "text":
            soup = makeHTMLRequest(f"https://www.{domain}&q={quote(query)}&start={p}&lr={lang}&safe={safe}")
        else:
            return "Invalid search type"
    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message}), 500

    # retrieve links
    result_divs = soup.findAll("div", {"class": "yuRUbf"})
    links = [div.find("a") for div in result_divs]
    hrefs = [link.get("href") for link in links]

    # retrieve title
    h3 = [div.find("h3") for div in result_divs]
    titles = [titles.text.strip() for titles in h3]

    # retrieve description
    result_desc = soup.findAll("div", {"class": "VwiC3b"})
    descriptions = [descs.text.strip() for descs in result_desc]

    # retrieve sublinks
    try:
        result_sublinks = soup.findAll("tr", {"class": lambda x: x and x.startswith("mslg")})
        sublinks_divs = [sublink.find("div", {"class": "zz3gNc"}) for sublink in result_sublinks]
        sublinks = [sublink.text.strip() for sublink in sublinks_divs]
        sublinks_links = [sublink.find("a") for sublink in result_sublinks]
        sublinks_hrefs = [link.get("href") for link in sublinks_links]
        sublinks_titles = [title.text.strip() for title in sublinks_links]
    except:
        sublinks = ""
        sublinks_hrefs = ""
        sublinks_titles = ""

    # retrieve kno-rdesc
    try:
        rdesc = soup.find("div", {"class": "kno-rdesc"})
        span_element = rdesc.find("span")
        kno = span_element.text
        desc_link = rdesc.find("a")
        kno_link = desc_link.get("href")
    except:
        kno = ""
        kno_link = ""

    # retrieve kno-title
    try:  # look for the title inside of a span in div.SPZz6b
        rtitle = soup.find("div", {"class": "SPZz6b"})
        rt_span = rtitle.find("span")
        rkno_title = rt_span.text.strip()
        # if we didn't find anyhing useful, move to next tests
        if rkno_title in ["", "See results about"]:
            raise
    except:
        for ellement, class_name in zip(["div", "span", "div"], ["DoxwDb", "yKMVIe", "DoxwDb"]):
            try:
                rtitle = soup.find(ellement, {"class": class_name})
                rkno_title = rtitle.text.strip()
            except:
                continue  # couldn't scrape anything. continue if we can.
            else:
                if rkno_title not in ["", "See results about"]:
                    break  # we got one
        else:
            rkno_title = ""

    # retrieve featured snippet
    try:
        featured_snip = soup.find("span", {"class": "hgKElc"})
        snip = featured_snip.text.strip()
    except:
        snip = ""

    # retrieve spell check
    try:
        spell = soup.find("a", {"class": "gL9Hy"})
        check = spell.text.strip()
    except:
        check = ""
    if search_type == "reddit":
        check = check.replace("site:reddit.com", "").strip()

    # get image for kno try javascript version first
    if javascript == "enabled":
        if kno_link == "":
            kno_image = ""
            kno_title = ""
        else:
            kno_title = kno_link.split("/")[-1]
            kno_title = f"/wikipedia?q={kno_title}"
            kno_image = ""
    else:
        if kno_link == "":
            kno_image = ""
            kno_title = ""
        else:
            try:
                kno_title = kno_link.split("/")[-1]
                soup = makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={kno_title}&pithumbsize=500")
                data = json.loads(soup.text)
                img_src = data['query']['pages'][list(data['query']['pages'].keys())[0]]['thumbnail']['source']
                kno_image = [f"/img_proxy?url={img_src}"]
                kno_image = ''.join(kno_image)
            except:
                kno_image = ""

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

    # list
    results = []
    for href, title, desc in zip(hrefs, titles, descriptions):
        results.append([unquote(href), title, desc])
    sublink = []
    for sublink_href, sublink_title, sublink_desc in zip(sublinks_hrefs, sublinks_titles, sublinks):
        sublink.append([sublink_href, sublink_title, sublink_desc])

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    current_url = request.url

    if "exported_math_expression" not in locals():
        exported_math_expression = ""

    if api == "true" and API_ENABLED == True:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        if search_type == "reddit":
            type = "reddit"
        else:
            type = "text"
        return render_template("results.html",
                               results=results, sublink=sublink, p=p, title=f"{query} - Araa",
                               q=f"{query}", fetched=f"{elapsed_time:.2f}",
                               snip=f"{snip}", kno_rdesc=f"{kno}", rdesc_link=f"{unquote(kno_link)}",
                               kno_wiki=f"{kno_image}", rkno_title=f"{rkno_title}", kno_title=f"{kno_title}",
                               user_info=f"{info}", calc=f"{calc}", check=check, current_url=current_url,
                               theme=request.cookies.get('theme', DEFAULT_THEME), new_tab=request.cookies.get("new_tab"),
                               javascript=request.cookies.get('javascript', 'enabled'), DEFAULT_THEME=DEFAULT_THEME,
                               type=type, search_type=search_type, repo_url=REPO, lang=lang, safe=safe, commit=latest_commit(),
                               exported_math_expression=exported_math_expression, API_ENABLED=API_ENABLED,
                               TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, domain=domain, ux_lang=ux_lang, lang_data=lang_data
                               )
