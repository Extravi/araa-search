from flask import Flask, request, render_template, jsonify, Response, make_response, redirect
import requests
import random
import json
from urllib.parse import quote
from _config import *
from src import textResults, torrents, helpers, images, video

bfp = open("./bangs.json", "r")
bjson = json.load(bfp)
bfp.close()

SEARCH_BANGS = {}
for bang, url in bjson.items():
    SEARCH_BANGS[bang] = url

app = Flask(__name__, static_folder="static", static_url_path="")
app.jinja_env.filters['highlight_query_words'] = helpers.highlight_query_words
app.jinja_env.globals.update(int=int)

COMMIT = helpers.latest_commit()


@app.route('/settings')
def settings():
    # default theme if none is set
    theme = request.cookies.get('theme', DEFAULT_THEME)
    lang = request.cookies.get('lang')
    safe = request.cookies.get('safe')
    new_tab = request.cookies.get('new_tab')
    domain = request.cookies.get('domain')
    javascript = request.cookies.get('javascript', 'enabled')

    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    return render_template('settings.html',
                           theme=theme,
                           lang=lang,
                           ux_lang=ux_lang,
                           lang_data=lang_data,
                           safe=safe,
                           new_tab=new_tab,
                           domain=domain,
                           javascript=javascript,
                           commit=COMMIT,
                           repo_url=REPO,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED
                           )

@app.route('/discover')
def discover():
    # default theme if none is set
    theme = request.cookies.get('theme', DEFAULT_THEME)
    javascript = request.cookies.get('javascript', 'enabled')

    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    return render_template('discover.html',
                           theme=theme,
                           javascript=javascript,
                           ux_lang=ux_lang,
                           lang_data=lang_data,
                           commit=COMMIT,
                           repo_url=REPO,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED
                           )


@app.route('/save-settings', methods=['POST'])
def save_settings():
    cookies = ['safe', 'javascript', 'domain', 'theme', 'lang', 'ux_lang', 'new_tab']

    response = make_response(redirect(request.referrer))
    for cookie in cookies:
        cookie_status = request.form.get(cookie)
        if cookie_status is not None:
            response.set_cookie(cookie, cookie_status,
                                max_age=COOKIE_AGE, httponly=False, 
                                secure=app.config.get("HTTPS")
                                )
    response.headers["Location"] = request.form.get('past')

    return response


@app.route("/suggestions")
def suggestions():
    query = request.args.get("q", "").strip()
    response = requests.get(f"https://ac.duckduckgo.com/ac?q={quote(query)}&type=list")
    return json.loads(response.text)


@app.route("/wikipedia")
def wikipedia():
    query = request.args.get("q", "").strip()
    response = helpers.makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={query}&pithumbsize=500")
    return json.loads(response.text)


@app.route("/api")
def api():
    if API_ENABLED == True:
        query = request.args.get("q", "").strip()
        t = request.args.get("t", "text").strip()
        p = (request.args.get('p', 1))
        try:
            response = requests.get(f"http://localhost:{PORT}/search?q={query}&t={t}&api=true&p={p}")
            return json.loads(response.text)
        except Exception as e:
            app.logger.error(e)
            return jsonify({"error": "An error occurred while processing the request"}), 500
    else:
        return jsonify({"error": "API disabled by instance operator"}), 503


@app.route("/img_proxy")
def img_proxy():
    # Get the URL of the image to proxy

    url = request.args.get("url", "").strip()

    # Only allow proxying image from startpage.com, upload.wikimedia.org and imgs.search.brave.com
    if not (url.startswith("https://s1.qwant.com/") or url.startswith("https://s2.qwant.com/") or url.startswith("https://upload.wikimedia.org/wikipedia/commons/") or url.startswith(f"https://{INVIDIOUS_INSTANCE}")):
        return Response("Error: invalid URL", status=400)

    # Choose one user agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    # Fetch the image data from the specified URL
    response = requests.get(url, headers=headers)

    # Check that the request was successful
    if response.status_code == 200:
        # Create a Flask response with the image data and the appropriate Content-Type header
        return Response(response.content, mimetype=response.headers["Content-Type"])
    else:
        # Return an error response if the request failed
        return Response("Error fetching image", status=500)


@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    # Searching only takes in GET requests. Return early if the request is anything but GET.
    if request.method != "GET":
        return Response(f"Error; expected GET request, got {request.method}", status=400)

    lang = request.cookies.get('lang')
    domain = request.cookies.get('domain')

    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # get the `q` query parameter from the URL
    query = request.args.get("q", "").strip()
    if query == "":
        if request.cookies.get('theme', DEFAULT_THEME) == 'dark_blur':
            css_style = "dark_blur_beta.css"
        else:
            css_style = None
        return render_template("search.html", theme = request.cookies.get('theme', DEFAULT_THEME),
            javascript=request.cookies.get('javascript', 'enabled'), DEFAULT_THEME=DEFAULT_THEME,
            css_style=css_style, repo_url=REPO, commit=COMMIT, API_ENABLED=API_ENABLED,
            lang=lang, domain=domain, lang_data=lang_data, ux_lang=ux_lang)

    # Check if the query has a bang.
    if BANG in query:
        query += " " # Simple fix to avoid a possible error 500
                     # when parsing the query for the bangkey.
        bang_index = query.index(BANG)
        bangkey = query[bang_index + len(BANG):query.index(" ", bang_index)].lower()
        if SEARCH_BANGS.get(bangkey) is not None:
            query = query.lower().replace(BANG + bangkey, "").lstrip()
            query = quote(query) # Quote the query to redirect properly.
            return app.redirect(SEARCH_BANGS[bangkey].format(query))
        # Remove the space at the end of the query.
        # The space was added to fix a possible error 500 when
        # parsing the query for the bangkey.
        query = query[:len(query) - 1]

    # type of search (text, image, etc.)
    type = request.args.get("t", "text")

    # render page based off of type
    # NOTE: Python 3.10 needed for a match statement!
    match type:
        case "torrent":
            return torrents.torrentResults(query)
        case "video":
            return video.videoResults(query)
        case "image":
            return images.imageResults(query)
        case _:
            return textResults.textResults(query)


if __name__ == "__main__":
    app.run(threaded=True, port=PORT)
