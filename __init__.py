from flask import Flask, request, render_template, jsonify, Response, make_response, redirect
import requests
import httpx
import trio
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

# Debug code uncomment when needed
#import logging, timeit
#logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Force all requests to only use IPv4
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# Force all HTTPX requests to only use IPv4
transport = httpx.HTTPTransport(local_address="0.0.0.0")

# Pool limit configuration
limits = httpx.Limits(max_keepalive_connections=None, max_connections=None, keepalive_expiry=None)

# Make persistent request sessions
s = requests.Session() # generic
ac = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # ac
googleac = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # googleac
wikimedia = requests.Session() # wikimedia
bing = requests.Session() # bing
piped = requests.Session() # piped

# Set a custom request header for the autocomplete session
ac.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/121.0"'})
googleac.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/121.0"'})


@app.route('/settings')
def settings():
    settings = helpers.Settings()

    # get user language settings
    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # Upgrade the request URL to https as to prevent a redirection error with /save-settings.
    if not request.is_secure:
        request.url = f"https://{request.host}/settings{f'?{request.query_string.decode()}' if request.query_string.decode() else ''}"

    return render_template('settings.html',
                           commit=COMMIT,
                           repo_url=REPO,
                           donate_url=DONATE,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED,
                           settings=settings,
                           lang_data=lang_data,
                           UX_LANGUAGES=UX_LANGUAGES
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
                           donate_url=DONATE,
                           current_url=request.url,
                           API_ENABLED=API_ENABLED,
                           settings=settings
                           )


@app.route('/save-settings', methods=['POST'])
def save_settings():
    cookies = ['safe', 'javascript', 'domain', 'theme', 'lang', 'ux_lang', 'new_tab', 'method', 'ac']

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
    # get user autocomplete settings
    settings = helpers.Settings()

    if request.method == "GET":
        query = request.args.get("q", "").strip()
    else:
        query = request.form.get("q", "").strip()

    if settings.ac == "ddg":
        response = ac.get(f"https://ac.duckduckgo.com/ac?q={quote(query)}&type=list")
        return json.loads(response.text)

    response = googleac.get(f"https://suggestqueries.google.com/complete/search?client=firefox&q={quote(query)}")
    suggestions_list = json.loads(response.text)

    # remove items at index 2 and 3
    if len(suggestions_list) > 2:
        suggestions_list.pop(3)
    if len(suggestions_list) > 2:
        suggestions_list.pop(2)

    # limit results
    suggestions_list[1] = suggestions_list[1][:8]
    return jsonify(suggestions_list)


@app.route("/wikipedia")
def wikipedia():
    if request.method == "GET":
        query = request.args.get("q", "").strip()
    else:
        query = request.form.get("q", "").strip()
    response, _ = helpers.makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={quote(query)}&pithumbsize=500", is_wiki=True)
    return json.loads(response.text)


@app.route("/api")
def api():
    if not API_ENABLED:
        return jsonify({"error": "API disabled by instance operator"}), 503
    if request.method == "GET":
        args = request.args
    else:
        args = request.form
    query = args.get("q", "").strip()
    t = args.get("t", "text").strip()
    p = args.get("p", 0)
    try:
        response = requests.get(f"http://localhost:{PORT}/search?q={quote(query)}&t={t}&api=true&p={p}")
        return json.loads(response.text)
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while processing the request"}), 500


@app.route("/img_proxy")
def img_proxy():
    # Get the URL of the image to proxy

    if request.method == "GET":
        url = request.args.get("url", "").strip()
    else:
        url = request.form.get("url", "").strip()

    # Only allow proxying image from qwant.com,
    # upload.wikimedia.org, and the default piped instance
    if not url.startswith(("https://tse.mm.bing.net/",
                           "https://tse1.explicit.bing.net/",
                           "https://tse2.explicit.bing.net/",
                           "https://tse3.explicit.bing.net/",
                           "https://tse4.explicit.bing.net/",
                           "https://upload.wikimedia.org/wikipedia/commons/",
                           "https://upload.wikimedia.org/wikipedia/en/thumb",
                           f"https://{PIPED_INSTANCE_PROXY}")
                          ):
        return Response("Error: invalid URL", status=400)

    # Choose one user agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    # Fetch the image data from the specified URL
    if url.startswith(("https://tse.mm.bing.net/",
                        "https://tse1.explicit.bing.net/",
                        "https://tse2.explicit.bing.net/",
                        "https://tse3.explicit.bing.net/",
                        "https://tse4.explicit.bing.net/")
                        ):
        response = bing.get(url, headers=headers)
    elif url.startswith("https://upload.wikimedia.org/wikipedia/commons/"):
        response = wikimedia.get(url, headers=headers)
    elif url.startswith(f"https://{PIPED_INSTANCE_PROXY}"):
        response = piped.get(url, headers=headers)
    else:
        response = s.get(url, headers=headers)

    # Check that the request was successful
    if response.status_code == 200:
        # Create a Flask response with the image data and the appropriate Content-Type header
        return Response(response.content, mimetype=response.headers["Content-Type"])
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
            repo_url=REPO, donate_url=DONATE, commit=COMMIT, API_ENABLED=API_ENABLED,
            lang_data=lang_data, settings=settings)

    # Search bangs.
    bang_index = -1
    while (bang_index := query.find(BANG, bang_index + 1, len(query))) != -1:
        if bang_index > 0 and query[bang_index - 1].strip() != "":
            continue
        query += " " # Simple fix to avoid a possible error 500
                     # when parsing the query for the bangkey.
        bangkey = query[bang_index + len(BANG):query.index(" ", bang_index)].lower()
        query = query[:len(query) - 1]
        if (bang_url := SEARCH_BANGS.get(bangkey)) is not None:
            # strip bang from query
            query = query[:bang_index] + query[bang_index + len(BANG + bangkey) + 1:]
            query = quote(query.strip())  # ensure query is quoted to redirect properly.
            return app.redirect(bang_url.format(q=query))

    # type of search (text, image, etc.)
    type = args.get("t", "text")

    # render page based off of type
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
