from flask import Flask, request, render_template, jsonify, Response, make_response, redirect, url_for, Markup, escape
import requests
import random
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import quote, unquote
import re
from os.path import exists
from _config import *
import base64

bfp = open("./bangs.json", "r")
bjson = json.load(bfp)
bfp.close()

SEARCH_BANGS = {}
for bang, url in bjson.items():
    SEARCH_BANGS[bang] = url

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

if exists("./.git/refs/heads/main"):
    with open('./.git/refs/heads/main') as f:
        COMMIT = f.readline()
        f.close()
else:
    COMMIT = "Not in main branch"

def makeHTMLRequest(url: str):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab HTML content
    html = requests.get(url, headers=headers)

    # Return the BeautifulSoup object
    return BeautifulSoup(html.text, "lxml")

@app.route('/settings')
def settings():
    # default theme if none is set
    theme = request.cookies.get('theme', DEFAULT_THEME)
    lang = request.cookies.get('lang')
    safe = request.cookies.get('safe')
    new_tab = request.cookies.get('new_tab')
    domain = request.cookies.get('domain')
    return render_template('settings.html',
                           theme=theme,
                           lang=lang,
                           safe=safe,
                           new_tab=new_tab,
                           domain=domain,
                           commit=COMMIT,
                           repo_url=REPO,
                           current_url=request.url
                           )

@app.route('/save-settings', methods=['POST'])
def save_settings():
    # get the selected theme from the form
    theme = request.form.get('theme')
    lang = request.form.get('lang')
    safe = request.form.get('safe')
    new_tab = request.form.get('new_tab')
    domain = request.form.get('domain')
    past_location = request.form.get('past')

    # set the theme cookie
    response = make_response(redirect(request.referrer))
    response.set_cookie('safe', safe, max_age=COOKIE_AGE, httponly=True, secure=app.config.get("HTTPS")) # set the cookie to never expire
    if domain is not None:
        response.set_cookie('domain', domain, max_age=COOKIE_AGE, httponly=True, secure=app.config.get("HTTPS"))
    if theme is not None:
        response.set_cookie('theme', theme, max_age=COOKIE_AGE, httponly=True, secure=app.config.get("HTTPS"))
    if lang is not None:
        response.set_cookie('lang', lang, max_age=COOKIE_AGE, httponly=True, secure=app.config.get("HTTPS"))
    if new_tab is not None:
        response.set_cookie('new_tab', new_tab, max_age=COOKIE_AGE, httponly=True, secure=app.config.get("HTTPS"))
    response.headers["Location"] = past_location

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
    domain = request.cookies.get('domain', 'google.com/search?gl=us')

    try:
        # search query
        if search_type == "reddit":
            site_restriction = "site:reddit.com"
            query_for_request = f"{query} {site_restriction}"
            soup = makeHTMLRequest(f"https://www.{domain}&q={query_for_request}&start={p}&lr={lang}")
        elif search_type == "text":
            soup = makeHTMLRequest(f"https://www.{domain}&q={query}&start={p}&lr={lang}&safe={safe}")
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

    # get image for kno
    if kno_link == "":
        kno_image = ""
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

    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        if search_type == "reddit":
            type = "reddit"
        else:
            type = "text"
        return render_template("results.html",
                               results=results, sublink=sublink, p=p, title=f"{query} - TailsX",
                               q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                               snip=f"{snip}", kno_rdesc=f"{kno}", rdesc_link = f"{unquote(kno_link)}",
                               kno_wiki=f"{kno_image}", rkno_title=f"{rkno_title}", user_info=f"{info}",
                               check=check, current_url=current_url, theme=request.cookies.get('theme', DEFAULT_THEME),
                               new_tab=request.cookies.get("new_tab"), DEFAULT_THEME=DEFAULT_THEME, type=type,
                               search_type=search_type, repo_url=REPO, lang=lang, safe=safe, commit=COMMIT
                               )

@app.route("/img_proxy")
def img_proxy():
    # Get the URL of the image to proxy
    url = request.args.get("url", "").strip()

    # Only allow proxying image from startpage.com, upload.wikimedia.org and imgs.search.brave.com
    if not (url.startswith("https://s1.qwant.com/") or url.startswith("https://s2.qwant.com/") or url.startswith("https://upload.wikimedia.org/wikipedia/commons/") or url.startswith("https://yt.revvy.de")):
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
    images = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]

    # decode urls 
    links = [a['href'] for a in ellements[0].findAll('a') if a.has_attr('href')]
    links = [url.split("?position")[0].split("==/")[-1] for url in links]
    links = [unquote(base64.b64decode(link).decode('utf-8')) for link in links]

    # list
    results = []
    for image, link in zip(images, links):
        results.append((image, link))

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
            type = "image", new_tab=request.cookies.get("new_tab"), repo_url = REPO, commit = COMMIT) 
    
def videoResults(query) -> Response:
    # remember time we started
    start_time = time.time()
    
    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://{INVIDIOUS_INSTANCE}/api/v1/search?q={query}")
    data = json.loads(soup.text)

    # sort by videos only
    videos = [item for item in data if item.get("type") == "video"]
    
    # retrieve links
    ytIds = [video["videoId"] for video in videos]
    hrefs = [f"https://{INVIDIOUS_INSTANCE}/watch?v={ytId}" for ytId in ytIds]
    
    # retrieve title
    title = [title["title"] for title in videos]
    
    # retrieve date
    date_span = [date["publishedText"] for date in videos]
    
    # retrieve views
    views = [views["viewCountText"] for views in videos]
    
    # retrieve creator
    creator_text = [creator_text["author"] for creator_text in videos]
    
    # retrieve publisher
    publisher_text = [f"YouTube" for creator in videos]
    
    # retrieve images
    video_thumbnails = [item['videoThumbnails'] for item in data if item.get('type') == 'video']
    maxres_thumbnails = [thumbnail for thumbnails in video_thumbnails for thumbnail in thumbnails if thumbnail['quality'] == 'maxresdefault']
    filtered_urls = ['/img_proxy?url=' + thumbnail['url'].replace(":3000", "").replace("http://", "https://") for thumbnail in maxres_thumbnails]
    
    # retrieve time
    duration = [duration["lengthSeconds"] for duration in videos]
    formatted_durations = [f"{duration // 60:02d}:{duration % 60:02d}" for duration in duration]
    
    # list
    results = []
    for href, title, date, view, creator, publisher, image, duration in zip(hrefs, title, date_span, views, creator_text, publisher_text, filtered_urls, formatted_durations):
        results.append([href, title, date, view, creator, publisher, image, duration])
        
    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time
     
    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("videos.html",
                               results=results, title=f"{query} - TailsX",
                               q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                               theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME = DEFAULT_THEME,
                               new_tab=request.cookies.get("new_tab"), type="video", repo_url=REPO, commit=COMMIT
                               )

def torrentResults(query) -> Response:
    # remember time we started
    start_time = time.time()
    
    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://torrentgalaxy.to/torrents.php?search={query}#results")

    result_divs = soup.findAll("div", {"class": "tgxtablerow"})
    title = [div.find("div", {"id": "click"}) for div in result_divs]
    title = [title.text.strip() for title in title]
    hrefs = [f"torrentgalaxy.to" for title in title]
    magnet_links = [div.find("a", href=lambda href: href and href.startswith("magnet")).get("href") for div in result_divs]
    file_sizes = [div.find("span", {"class": "badge-secondary"}).text.strip() for div in result_divs]
    view_counts = [div.find("font", {"color": "orange"}).text.strip() for div in result_divs]
    seeders = [div.find("font", {"color": "green"}).text.strip() for div in result_divs]
    leechers = [div.find("font", {"color": "#ff0000"}).text.strip() for div in result_divs]

    # list
    results = []
    for href, title, magnet_link, file_size, view_count, seeder, leecher in zip(hrefs, title, magnet_links, file_sizes, view_counts, seeders, leechers):
        results.append([href, title, magnet_link, file_size, view_count, seeder, leecher])
        
    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time
     
    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("torrents.html",
                               results=results, title=f"{query} - TailsX",
                               q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                               theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME = DEFAULT_THEME,
                               type="torrent", repo_url=REPO, commit=COMMIT
                               )

@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        # get the `q` query parameter from the URL
        query = request.args.get("q", "").strip()
        if query == "":
            if request.cookies.get('theme', DEFAULT_THEME) == 'dark_blur':
                css_style = "dark_blur_beta.css"
            else:
                css_style = None
            return render_template("search.html", theme = request.cookies.get('theme', DEFAULT_THEME),
                DEFAULT_THEME=DEFAULT_THEME, css_style=css_style, repo_url = REPO, commit = COMMIT)

        # Check if the query has a bang.
        if query.startswith(BANG):
            query += " " # Simple fix to avoid a possible error 500
                         # when parsing the query for the bangkey.
            bangkey = query[len(BANG):query.index(" ")].lower()
            if SEARCH_BANGS.get(bangkey) != None:
                query = query.lower().removeprefix(BANG + bangkey).lstrip()
                return app.redirect(SEARCH_BANGS[bangkey].format(query))
            # Remove the space at the end of the query.
            # The space was added to fix a possible error 500 when
            # parsing the query for the bangkey.
            query = query[:len(query)-1]

        # type of search (text, image, etc.)
        type = request.args.get("t", "text")

        # render page based off of type
        # NOTE: Python 3.10 needed for a match statement!
        match type:
            case "torrent":
                return torrentResults(query)
            case "video":
                return videoResults(query)
            case "image":
                return imageResults(query)
            case _:
                return textResults(query)

if __name__ == "__main__":
    app.run(threaded=True, port=PORT)
