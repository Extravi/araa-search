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
    settings = helpers.Settings()

    # get user language settings
    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    return render_template('settings.html',
                           commit=COMMIT,
                           repo_url=REPO,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED,
                           settings=settings,
                           lang_data=lang_data
                           )

@app.route('/discover')
def discover():
    settings = helpers.Settings()

    # get user language settings
    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    return render_template('discover.html',
                           lang_data=lang_data,
                           commit=COMMIT,
                           repo_url=REPO,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED,
                           settings=settings
                           )


@app.route('/save-settings', methods=['POST'])
def save_settings():
    cookies = ['safe', 'javascript', 'domain', 'theme', 'lang', 'ux_lang', 'new_tab', 'method']

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
    if request.method == "GET":
        query = request.args.get("q", "").strip()
    else:
        query = request.form.get("q", "").strip()
    response = requests.get(f"https://ac.duckduckgo.com/ac?q={quote(query)}&type=list")
    return json.loads(response.text)


@app.route("/wikipedia")
def wikipedia():
    if request.method == "GET":
        query = request.args.get("q", "").strip()
    else:
        query = request.form.get("q", "").strip()
    response = helpers.makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={query}&pithumbsize=500")
    return json.loads(response.text)


@app.route("/api")
def api():
    if API_ENABLED:
        if request.method == "GET":
            args = request.args
        else:
            args = request.form
        query = args.get("q", "").strip()
        t = args.get("t", "text").strip()
        p = args.get('p', 1)
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

    if request.method == "GET":
        url = request.args.get("url", "").strip()
    else:
        url = request.form.get("url", "").strip()

    # Only allow proxying image from qwant.com,
    # upload.wikimedia.org, and the default invidious instance
    if not url.startswith(("https://s1.qwant.com/", "https://s2.qwant.com/",
                           "https://upload.wikimedia.org/wikipedia/commons/",
                           f"https://{INVIDIOUS_INSTANCE}")
                          ):
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
    # Return early if the request is anything but GET or POST.
    if request.method not in ["POST", "GET"]:
        return Response(
            f"Error; expected GET or POST request, got {request.method}",
            status=400
        )

    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    settings = helpers.Settings()

    # get user language settings
    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # get the `q` query parameter from the URL
    query = args.get("q", "").strip()
    if query == "":
        return render_template("search.html",
            repo_url=REPO, commit=COMMIT, API_ENABLED=API_ENABLED,
            lang_data=lang_data, settings=settings)

    # Check if the query has a bang.
    if BANG in query:
        query += " " # Simple fix to avoid a possible error 500
                     # when parsing the query for the bangkey.
        bang_index = query.index(BANG)
        bangkey = query[bang_index + len(BANG):query.index(" ", bang_index)].lower()
        if SEARCH_BANGS.get(bangkey) is not None:
            query = query.lower().replace(BANG + bangkey, "").lstrip()
            query = quote(query)  # Quote the query to redirect properly.
            return app.redirect(SEARCH_BANGS[bangkey].format(query))
        # Remove the space at the end of the query.
        # The space was added to fix a possible error 500 when
        # parsing the query for the bangkey.
        query = query[:len(query) - 1]

    # type of search (text, image, etc.)
    type = args.get("t", "text")

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
