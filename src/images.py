from src.helpers import makeHTMLRequest, latest_commit
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response, redirect
import time
import json
from urllib.parse import quote
import base64

def generate_proxy_link(link):
    link = link.split("?position")[0].split("==/")[-1]
    return unquote(base64.b64decode(link).decode('utf-8'))

def imageResults(query, api=False) -> Response:
    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    try:
        p = int(request.args.get('p', 1))
        if p < 1:
            p = 1
        else:
            p = int(request.args.get('p', 1))
    except:
        return redirect('/search')   

    # grab & format webpage
    soup = makeHTMLRequest(f"https://lite.qwant.com/?q={quote(query)}&t=images&p={p}")
    results = []

    for image in soup.select(".images-container a"):
        original_image = image.find("img")

        results.append({
            "origin_link": generate_proxy_link(image["href"]),
            "image_source": f"/img_proxy?url={quote(original_image['src'])}",
            "desc": original_image['alt']
        })

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results=results, title=f"{query} - Araa",
            q=f"{query}", fetched=f"{elapsed_time:.2f}",
            theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
            javascript=request.cookies.get('javascript', 'enabled'), type="image",
            new_tab=request.cookies.get("new_tab"), repo_url=REPO, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, ux_lang=ux_lang, lang_data=lang_data, 
            commit=latest_commit())
