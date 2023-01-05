from flask import Flask, request, render_template, jsonify, Response, make_response, redirect, url_for
import requests
import random
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import quote

app = Flask(__name__, static_folder="static", static_url_path="")

PORT = 8000

def makeHTMLRequest(url: str) -> Response:
    # Useragents to use in the request.
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    ]

    # Choose one at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab HTML content
    html = requests.get(url, headers = headers)

    # Return the HTML in an easy to parse object
    return BeautifulSoup(html.text, "lxml")

# default theme
DEFAULT_THEME = 'dark'

@app.route('/settings')
def settings():
    # default theme if none is set
    theme = request.cookies.get('theme', DEFAULT_THEME)
    return render_template('settings.html', theme=theme)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    # get the selected theme from the form
    theme = request.form.get('theme')

    # set the theme cookie
    response = make_response(redirect(url_for('settings')))
    response.set_cookie('theme', theme, max_age=2147483647) # set the cookie to never expire

    return response

@app.route("/suggestions")
def suggestions():
    query = request.args.get("q", "").strip()
    response = requests.get(f"https://ac.duckduckgo.com/ac?q={query}&type=list")
    return json.loads(response.text)

@app.route("/api")
def api():
    query = request.args.get("q", "").strip()
    try:
        response = requests.get(f"http://localhost:{PORT}/search?q={query}&api=true")
        return json.loads(response.text)
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while processing the request"}), 500

def textResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")

    # search query
    soup = makeHTMLRequest(f"https://www.google.com/search?q={query}")

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

    # retrieve featured snippet
    try:
        featured_snip = soup.find("span", {"class": "hgKElc"})
        snip = featured_snip.text.strip()
    except:
        snip = ""
        
    # gets users ip or user agent
    info = ""
    if "what is my ip" in query.lower() or "what is my ip address" in query.lower():
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            ip = xff.split(",")[-1].strip()
        else:
            ip = request.remote_addr or "unknown"
        info = ip
    elif "what is my user agent" in query.lower() or "what is my useragent" in query.lower():
        user_agent = request.headers.get("User-Agent") or "unknown"
        info = user_agent

    # list
    results = []
    for href, title, desc in zip(hrefs, titles, descriptions):
        results.append([href, title, desc])

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("results.html", results = results, title = f"{query} - TailsX",
            q = f"{query}", fetched = f"Fetched the results in {elapsed_time:.2f} seconds",
            snip = f"{snip}", kno_rdesc = f"{kno}", rdesc_link = f"{kno_link}", user_info=f"{info}", theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME)

@app.route("/img_proxy")
def img_proxy():
    # Get the URL of the image to proxy
    url = request.args.get("url", "").strip()

    # Only allow proxying images from startpage.com
    if not url.startswith("https://www.startpage.com/"):
        return Response("Error: invalid URL", status=400)

    # Fetch the image data from the specified URL
    response = requests.get(url)

    # Check that the request was successful
    if response.status_code == 200:
        # Create a Flask response with the image data and the appropriate Content-Type header
        return Response(response.content, mimetype=response.headers["Content-Type"])
    else:
        # Return an error response if the request failed
        return Response("Error fetching image", status=500)

def imageResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    # grab & format webpage
    soup = makeHTMLRequest(f"https://www.startpage.com/sp/search?query={query}&cat=images")

    # get 'img' ellements
    ellements = soup.findAll("img", {"class": "css-6a21sa"})
    # get source urls
    image_sources = [f"https://www.startpage.com/{ell['src']}" for ell in ellements]
    # generate results
    results = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    return render_template("images.html", results = results, title = f"{query} - TailsX",
        q = f"{query}", fetched = f"Fetched the results in {elapsed_time:.2f} seconds", theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME)
    
def videoResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    # grab & format webpage
    soup = makeHTMLRequest(f"https://search.brave.com/videos?q={query}&source=web")
    
    # retrieve links
    card_divs = soup.findAll("div", {"class": "card"})
    links = [div.find("a") for div in card_divs]
    hrefs = [link.get("href") for link in links]
    
    # retrieve title
    title = [div.find("div", {"class": "title"}).text.strip() for div in card_divs]
    
    # retrieve date
    date_span = [div.find('span').text.strip() for div in card_divs]
    
    # retrieve views
    views_divs = soup.findAll('div', class_='stat')
    views = [div.get('title') for div in views_divs]
    
    # retrieve creator
    creator = soup.findAll('div', class_='creator ellipsis')
    creator_text = [div.text.strip() for div in creator]
    
    # retrieve publisher
    publisher = soup.findAll('div', class_='ellipsis')
    publisher_text = [div.text.strip() for div in publisher]
    
    # list
    results = []
    for href, title, date, view, creator, publisher in zip(hrefs, title, date_span, views, creator_text, publisher_text):
        results.append([href, title, date, view, creator, publisher])
        
    return jsonify(results)

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        # get the `q` query parameter from the URL
        query = request.args.get("q", "").strip()
        if query == "":
            return render_template("search.html", theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME)

        # type of search (text, image, etc.)
        type = request.args.get("t", "text")

        # render page based off of type
        # NOTE: Python 3.10 needed for a match statement!
        match type:
            case "video":
                return videoResults(query)
            case "image":
                return imageResults(query)
            case _:
                return textResults(query)

if __name__ == "__main__":
    # WARN: run() is not intended to be used in a production setting!
    # see https://flask.palletsprojects.com/en/2.2.x/deploying/ for more info
    app.run(threaded=True, port=PORT)
