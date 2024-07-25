import random
import requests
import httpx
import trio
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from _config import *
from markupsafe import escape, Markup
from os.path import exists
from thefuzz import fuzz
from flask import request

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
google = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # google
wiki = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # wikipedia
piped = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # piped
qwant = httpx.Client(http2=True, follow_redirects=True, transport=transport, limits=limits)  # qwant

def makeHTMLRequest(url: str, is_google=False, is_wiki=False, is_piped=False):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    headers = {
        "User-Agent": random.choice(user_agents), # Choose a user-agent at random
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Dnt": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Grab HTML content with the specific cookie
    if is_google:
        html = google.get(url, headers=headers) # persistent session for google
    elif is_wiki:
        html = wiki.get(url, headers=headers) # persistent session for wikipedia
    elif is_piped:
        html = piped.get(url, headers=headers) # persistent session for piped
    else:
        html = s.get(url, headers=headers) # generic persistent session

    # Allow for callers to handle errors better
    content = None if html.status_code != 200 else BeautifulSoup(html.text, "lxml")

    # Return the BeautifulSoup object
    return (content, html.status_code)

# search highlights
def highlight_query_words(string, query):
    string = escape(string)
    query_words = query.lower().split()
    highlighted_words = []
    for word in string.split():
        for query_word in query_words:
            if fuzz.ratio(word.lower(), query_word) >= 80:
                highlighted_word = Markup(f'<span class="highlight">{word}</span>')
                highlighted_words.append(highlighted_word)
                break
        else:
            highlighted_words.append(word)
    highlighted = ' '.join(highlighted_words)
    return Markup(highlighted)


def latest_commit():
    if exists(".git/refs/heads/main"):
        with open('./.git/refs/heads/main') as f:
            return f.readline()
    return "Not in main branch"

def makeJSONRequest(url: str, is_qwant=False):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab json content
    if is_qwant:
        response = qwant.get(url, headers=headers) # persistent session for qwant
    else:
        response = s.get(url, headers=headers) # generic persistent session

    # Return the JSON object
    return (json.loads(response.text), response.status_code)

def get_magnet_hash(magnet):
    return magnet.split("btih:")[1].split("&")[0]

def get_magnet_name(magnet):
    return magnet.split("&dn=")[1].split("&tr")[0]


def apply_trackers(hash, name="", magnet=True):
    if magnet:
        name = get_magnet_name(hash)
        hash = get_magnet_hash(hash)

    return f"magnet:?xt=urn:btih:{hash}&dn={name}&tr={'&tr='.join(TORRENT_TRACKERS)}"

def string_to_bytes(file_size):
    units = {
        'bytes': 1,
        'kb': 1024,
        'mb': 1024 ** 2,
        'gb': 1024 ** 3,
        'tb': 1024 ** 4,
        'kib': 1024,
        'mib': 1024 ** 2,
        'gib': 1024 ** 3,
        'tib': 1024 ** 4
    }

    size, unit = file_size.lower().split()
    return float(size) * units[unit]

def bytes_to_string(size):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"

class Settings():
    def __init__(self):
        self.domain = request.cookies.get("domain", DEFAULT_GOOGLE_DOMAIN)
        self.javascript = request.cookies.get("javascript", "enabled")
        self.lang = request.cookies.get("lang", "")
        self.new_tab = request.cookies.get("new_tab", "")
        self.safe = request.cookies.get("safe", "active")
        self.ux_lang = request.cookies.get("ux_lang", DEFAULT_UX_LANG)
        self.theme = request.cookies.get("theme", DEFAULT_THEME)
        self.method = request.cookies.get("method", DEFAULT_METHOD)
        self.ac = request.cookies.get("ac", DEFAULT_AUTOCOMPLETE)

# Returns a tuple of two ellements.
# The first is the wikipedia proxy's URL (used to load an wiki page's image after page load),
# and the second is an image proxy link for the very image of the page itself.
# 
# Either the first or second ellement will be a string, but not both (at least one ellement
# will be None).
# 
# NOTE: This function may return (None, None) in cases of failure.
def grab_wiki_image_from_url(wikipedia_url: str, user_settings: Settings) -> tuple[str | None]:
    kno_title = None
    kno_image = None

    if user_settings.javascript == "enabled":
        kno_title = wikipedia_url.split("/")[-1]
        kno_title = f"/wikipedia?q={kno_title}"
    else:
        try:
            _kno_title = wikipedia_url.split("/")[-1]
            soup = makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={_kno_title}&pithumbsize=500", is_wiki=True)
            data = json.loads(soup.text)
            img_src = data['query']['pages'][list(data['query']['pages'].keys())[0]]['thumbnail']['source']
            _kno_image = [f"/img_proxy?url={img_src}"]
            _kno_image = ''.join(_kno_image)
        finally:
            kno_image = _kno_image

    return kno_title, kno_image
