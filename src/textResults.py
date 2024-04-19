from src import helpers
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
import re
from math import isclose # For float comparisons
from src.text_engines import google

def textResults(query) -> Response:
    # get user language settings
    settings = helpers.Settings()

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form
 
    with open(f'static/lang/{settings.ux_lang}.json', 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = args.get("api", "false")
    search_type = args.get("t", "text")
    p = args.get("p", 0)

    # search query
    if search_type == "reddit":
        query += "site:reddit.com"

    try:
        # TODO; perform searches
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
                               type=type, search_type=search_type, repo_url=REPO, donate_url=DONATE, commit=helpers.latest_commit(),
                               exported_math_expression=exported_math_expression, API_ENABLED=API_ENABLED,
                               TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
                               settings=settings,
                               )
