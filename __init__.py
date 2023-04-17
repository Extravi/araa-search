from flask import Flask, request, render_template, jsonify, Response, make_response, redirect, url_for, Markup, escape
import requests
import random
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import quote
import re

# search highlights
def highlight_query_words(string, query):
    query_words = [re.escape(word) for word in query.lower().split()]
    words = string.split()
    highlighted = []
    query_regex = re.compile('|'.join(query_words))
    highlighted_words = []
    for word in words:
        cleaned_word = word.strip().lower()
        if query_regex.search(cleaned_word) and cleaned_word not in highlighted:
            highlighted_words.append(Markup(f'<span class="highlight">{escape(word)}</span>'))
            highlighted.append(cleaned_word)
        else:
            highlighted_words.append(escape(word))
    return Markup(' '.join(highlighted_words))

app = Flask(__name__, static_folder="static", static_url_path="")
app.jinja_env.filters['highlight_query_words'] = highlight_query_words
app.jinja_env.globals.update(int=int)

PORT = 8000

# Useragents to use in the request.
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]

with open('./REPOSITORY') as f:
    REPO = f.readline()
    f.close()
with open('./.git/refs/heads/main') as f:
    COMMIT = f.readline()
    f.close()

def makeHTMLRequest(url: str) -> Response:
    # Choose a user-agent at random
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
    lang = request.cookies.get('lang')
    safe = request.cookies.get('safe')
    return render_template('settings.html', theme = theme, lang = lang, safe = safe, commit = COMMIT,
        repo_url = REPO)

@app.route('/save-settings', methods=['POST'])
def save_settings():
    # get the selected theme from the form
    theme = request.form.get('theme')
    lang = request.form.get('lang')
    safe = request.form.get('safe')

    # set the theme cookie
    response = make_response(redirect(url_for('settings')))
    response.set_cookie('theme', theme, max_age = 2147483647, httponly=True, secure=app.config.get("HTTPS")) # set the cookie to never expire
    response.set_cookie('lang', lang, max_age=2147483647, httponly=True, secure=app.config.get("HTTPS"))
    response.set_cookie('safe', safe, max_age=2147483647, httponly=True, secure=app.config.get("HTTPS"))

    return response

@app.route("/suggestions")
def suggestions():
    query = request.args.get("q", "").strip()
    response = requests.get(f"https://ac.duckduckgo.com/ac?q={query}&type=list")
    return json.loads(response.text)

@app.route("/api")
def api():
    query = request.args.get("q", "").strip()
    t = request.args.get("t", "text").strip()
    try:
        response = requests.get(f"http://localhost:{PORT}/search?q={query}&t={t}&api=true")
        return json.loads(response.text)
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while processing the request"}), 500

def textResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")
    search_type = request.args.get("t", "text")
    p = request.args.get("p", 0)
    lang = request.cookies.get('lang', '')
    safe = request.cookies.get('safe', 'active')

    # search query
    if search_type == "reddit":
        site_restriction = "site:reddit.com"
        query_for_request = f"{query} {site_restriction}"
        soup = makeHTMLRequest(f"https://www.google.com/search?q={query_for_request}&start={p}&lr={lang}")
    elif search_type == "text":
        soup = makeHTMLRequest(f"https://www.google.com/search?q={query}&start={p}&lr={lang}&safe={safe}")
    else:
        return "Invalid search type"

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
        rtitle = soup.find("div", {"class": "SPZz6b"})
        rtitle_span = rtitle.find("span")
        rkno_title = rtitle_span.text.strip()
    except:
        kno = ""
        kno_link = ""
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
        
    # get image for kno
    if kno_link == "":
        kno_image = ""
    else:
        try:
            kno_title = kno_link.split("/")[-1]
            soup = makeHTMLRequest(f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={kno_title}&pithumbsize=500")
            data = json.loads(soup.text)
            img_src = data['query']['pages'][list(data['query']['pages'].keys())[0]]['thumbnail']['source']
            kno_image = [f"/img_proxy?url={img_src}"]
            kno_image = ''.join(kno_image)
        except:
            kno_image = ""
        
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
    sublink = []
    for sublink_href, sublink_title, sublink_desc in zip(sublinks_hrefs, sublinks_titles, sublinks):
        sublink.append([sublink_href, sublink_title, sublink_desc])
             
    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        if search_type == "reddit":
            type = "reddit"
        else:
            type = "text"
        return render_template("results.html", results = results, sublink = sublink, p = p, title = f"{query} - TailsX",
            q = f"{query}", fetched = f"Fetched the results in {elapsed_time:.2f} seconds",
            snip = f"{snip}", kno_rdesc = f"{kno}", rdesc_link = f"{kno_link}", kno_wiki = f"{kno_image}", rkno_title = f"{rkno_title}", user_info = f"{info}", check = check,
            theme = request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME = DEFAULT_THEME,
            type = type, search_type = search_type, repo_url = REPO, commit = COMMIT)

@app.route("/img_proxy")
def img_proxy():
    # Get the URL of the image to proxy
    url = request.args.get("url", "").strip()

    # Only allow proxying image from startpage.com, upload.wikimedia.org and imgs.search.brave.com
    if not (url.startswith("https://s1.qwant.com/") or url.startswith("https://s2.qwant.com/") or url.startswith("https://upload.wikimedia.org/wikipedia/commons/") or url.startswith("https://imgs.search.brave.com")):
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

def imageResults(query) -> Response:
    # remember time we started
    start_time = time.time()
    
    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://lite.qwant.com/?q={query}&t=images")

    # get 'img' ellements
    ellements = soup.findAll("div", {"class": "images-container"})
    # get source urls
    image_sources = [a.find('img')['src'] for a in ellements[0].findAll('a') if a.find('img')]
    
    # generate results
    results = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results = results, title = f"{query} - TailsX",
            q = f"{query}", fetched = f"Fetched the results in {elapsed_time:.2f} seconds",
            theme = request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME = DEFAULT_THEME,
            type = "image", repo_url = REPO, commit = COMMIT) 
    
def videoResults(query) -> Response:
    # remember time we started
    start_time = time.time()
    
    api = request.args.get("api", "false")

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
    views = [div.find("div", class_='stat').get("title") if div.find("div", class_='stat') else "Not found" for div in soup.findAll('div', class_='card-footer')]
    
    # retrieve creator
    creator = soup.findAll('div', class_='creator ellipsis svelte-gzavkh')
    creator_text = [div.text.strip() for div in creator]
    
    # retrieve publisher
    publisher = soup.findAll('div', class_='publisher center-horizontally svelte-gzavkh')
    publisher_text = [div.text.strip() for div in publisher]
    
    # retrieve images
    image_divs = soup.findAll("div", {"class": "card-image svelte-gzavkh"})
    image_urls = [div.find("img", {"class": "svelte-gzavkh"}) for div in image_divs]
    image_urls = [div.get("src") for div in image_urls]

    # extract URLs from the "style" attribute
    urls = re.findall(r"https?://[^\s]+", " ".join(image_urls))

    # filter out URLs that match a specific pattern
    filtered_urls = [url for url in urls if not "cdn.search.brave.com" in url]
    filtered_urls = [url.replace("'),", "") for url in filtered_urls]
    filtered_urls = [f"/img_proxy?url={quote(img_src)}" for img_src in filtered_urls]
    
    # retrieve time
    duration = soup.findAll("div", {"class": "duration"})
    duration = [div.text.strip() for div in duration]
    
    # list
    results = []
    for href, title, date, view, creator, publisher, image, duration in zip(hrefs, title, date_span, views, creator_text, publisher_text, filtered_urls, duration):
        results.append([href, title, date, view, creator, publisher, image, duration])
        
    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time
     
    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("videos.html", results = results, title = f"{query} - TailsX",
            q = f"{query}", fetched = f"Fetched the results in {elapsed_time:.2f} seconds",
            theme = request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME = DEFAULT_THEME,
            type = "video", repo_url = REPO, commit = COMMIT)

# Search engine bangs for ppl who want to use another engine through TailsX's
# search bar.
# NOTE: Bangs are case insensitive!
# NOTE: The first brackets, "{}", is where the query will be put in the final URL.
# TODO: Bangs will ONLY redirect to TEXT results (type is dropped); maybe change this?
SEARCH_BANGS = [
    {'bang': 'g',     'url': 'https://www.google.com/search?q={}'},
    {'bang': 'ddg',   'url': 'https://duckduckgo.com/?q={}'},
    {'bang': 'brave', 'url': 'https://search.brave.com/search?q={}'},
    {'bang': 'bing',  'url': 'https://www.bing.com/search?q={}'},
]

# The char used to denote bangs (see above constant).
# EG BANG='!': "!ddg cats" will search "cats" on DuckDuckGo.
BANG = '!'

@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        # get the `q` query parameter from the URL
        query = request.args.get("q", "").strip()
        if query == "":
            return render_template("search.html", theme = request.cookies.get('theme', DEFAULT_THEME),
                DEFAULT_THEME=DEFAULT_THEME, repo_url = REPO, commit = COMMIT)

        # Check if the query has a bang.
        if query.startswith(BANG):
            for SEARCH_BANG in SEARCH_BANGS:
                # Check for a match.
                if query[len(BANG):].lower().startswith(SEARCH_BANG['bang']):
                    # Match found, redirect (removing bang from query).
                    query = query.lower().removeprefix(BANG + SEARCH_BANG['bang']).lstrip()
                    return app.redirect(SEARCH_BANG['url'].format(query))

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
