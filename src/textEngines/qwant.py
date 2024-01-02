from src import helpers
from flask import request, jsonify
from urllib.parse import quote, urlencode, urlparse


def search(settings):
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    url_args = {
        "t": "web",
        "q": args['q'],
        "count": 10,
        "locale": "en_GB",
        "offset": int(args.get("p", 0)),
        "safesearch": settings.safe
    }
    url = "https://api.qwant.com/v3/search/web?{}"
    json_data = helpers.makeJSONRequest(url.format(urlencode(url_args)))

    if json_data['status'] != "success":
        # Add error handling later
        return {}

    resp_results = json_data.get("data", {}).get("result", {}).get("items", {}).get("mainline")
    if resp_results is None:
        json_data
        return {}

    web_results = []
    for group in resp_results:
        if group.get("type") == "web":
            # Only get web results. No images/ads.
            web_results += group.get("items", [])

    results = []
    for result in web_results:
        if len(result['desc']) > 166:
            short_desc = result['desc'][:166] + "..."
        else:
            short_desc = result['desc']
        results.append({
            "href": result['source'],
            "title": result['title'],
            "full_desc": result['desc'],
            "desc": short_desc,
            "has_sublinks": False,
            "sublinks": []
        })

    spell = json_data['data']['query']['queryContext'].get('alteredQuery', '')

    return {
        "results": results,
        "snip": "",
        "check": spell,
        "wiki": wikipedia(web_results)
    }


def wikipedia(web_results):
    for result in web_results:
        parsed_url = urlparse(result['url'])
        if 'wikipedia.org' in parsed_url.netloc:
            image = result.get('thumbnailUrl', '')
            if image != "":
                image = f"/img_proxy?url={image}"
            print(image)
            return {
                "has_wiki": True,
                "title": result['title'],
                "description": result['desc'],
                "image": image,
                "link": result['url']
            }
    return {
        "has_wiki": False
    }
