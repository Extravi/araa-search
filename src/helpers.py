import random
import requests
import httpx
import trio
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, quote
from _config import *
from markupsafe import escape, Markup
from os.path import exists
from pathlib import Path
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
    domain = urlparse(unquote(url)).netloc
    if domain == "":
        raise Exception("Invalid URL.")
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
        html = google.get(url, headers=headers, timeout=20) # persistent session for google
    elif is_wiki:
        html = wiki.get(url, headers=headers, timeout=20) # persistent session for wikipedia
    elif is_piped:
        html = piped.get(url, headers=headers, timeout=20) # persistent session for piped
    else:
        html = s.get(url, headers=headers, timeout=20) # generic persistent session

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


def load_lang_data(ux_lang: str):
    # Language files are UTF-8 encoded. Always decode with UTF-8 so
    # non-English locales work on Windows systems using cp1252 defaults.
    selected_lang = (ux_lang or DEFAULT_UX_LANG).strip()
    if selected_lang == "":
        selected_lang = DEFAULT_UX_LANG

    lang_dir = Path("static") / "lang"
    selected_path = lang_dir / f"{selected_lang}.json"

    try:
        with open(selected_path, "r", encoding="utf-8") as file:
            return format_araa_name(json.load(file))
    except Exception as err:
        fallback_path = lang_dir / f"{DEFAULT_UX_LANG}.json"
        print(f"WARN: Failed to load UX language '{selected_lang}'. Falling back to '{DEFAULT_UX_LANG}'. ({err})")
        with open(fallback_path, "r", encoding="utf-8") as file:
            return format_araa_name(json.load(file))


def makeJSONRequest(url: str, is_qwant=False):
    # block unwanted request from an edited cookie
    domain = urlparse(unquote(url)).netloc
    if domain == "":
        raise Exception("Invalid URL.")
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab json content
    if is_qwant:
        response = qwant.get(url, headers=headers, timeout=20) # persistent session for qwant
    else:
        response = s.get(url, headers=headers, timeout=20) # generic persistent session

    # Try to parse JSON; if the response isn't valid JSON, return None and
    # log the response text for debugging instead of raising an exception.
    try:
        parsed = json.loads(response.text)
        return (parsed, response.status_code)
    except Exception as e:
        # Log useful debug information to the console so debugging is easier.
        try:
            print(f"[helpers.makeJSONRequest] Failed to parse JSON from {url} (status={response.status_code}):")
            # Truncate long responses to avoid huge logs
            preview = response.text[:2000]
            print(preview)
        except Exception:
            pass
        return (None, response.status_code)

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


def settings_lang_to_searx(settings_lang: str | None) -> str:
    # Convert Araa language cookie values to searxng language values.
    if settings_lang is None:
        return ""

    settings_lang = settings_lang.strip()
    if settings_lang == "":
        return ""

    # Keep compatibility with existing UI values.
    if settings_lang == "lang_zh-CN":
        return "zh_Hans"
    if settings_lang == "lang_zh-TW":
        return "zh_Hant"
    if settings_lang == "lang_iw":
        return "he"

    if settings_lang.startswith("lang_"):
        settings_lang = settings_lang[5:]

    if settings_lang.lower() == "iw":
        return "he"

    return settings_lang.lower()


def should_request_knowledge_panel(query: str, search_type: str, page_num: int = 1) -> bool:
    if not globals().get("LOCAL_SEARXNG_KNOWLEDGE_PANELS_ENABLED", True):
        return False

    if search_type != "text" or page_num != 1:
        return False

    query = (query or "").strip()
    if query == "":
        return False

    try:
        max_words = int(globals().get("LOCAL_SEARXNG_KNOWLEDGE_PANELS_MAX_QUERY_WORDS", 4))
    except Exception:
        max_words = 4

    if max_words < 1:
        max_words = 1

    if len(query.split()) > max_words:
        return False

    # Avoid operator-heavy / advanced query syntax where a panel is unlikely.
    lower_query = query.lower()
    if lower_query.startswith(("http://", "https://")):
        return False
    if re.search(r'(^|\s)(site|filetype|inurl|intitle|related|cache|after|before)\s*:', lower_query):
        return False

    return True


class Settings():
    def __init__(self):
        self.javascript = request.cookies.get("javascript", "enabled")
        self.lang = request.cookies.get("lang", "")
        self.new_tab = request.cookies.get("new_tab", "")
        self.safe = request.cookies.get("safe", "active")
        self.ux_lang = request.cookies.get("ux_lang", DEFAULT_UX_LANG)
        self.theme = request.cookies.get("theme", DEFAULT_THEME)
        self.method = request.cookies.get("method", DEFAULT_METHOD)
        self.ac = request.cookies.get("ac", DEFAULT_AUTOCOMPLETE)
        self.engine = request.cookies.get("engine", DEFAULT_ENGINE)
        self.image_engine = request.cookies.get("image_engine", "google")
        self.date_filter = request.cookies.get("date_filter", "collapsed")
        self.torrent = request.cookies.get("torrent", "enabled" if TORRENTSEARCH_ENABLED else "disabled")


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

    raw_url = str(wikipedia_url or "").strip()
    if raw_url == "" or raw_url.lower() in ["none", "null"]:
        return kno_title, kno_image

    # Extract title from urls like https://en.wikipedia.org/wiki/Telegram_(software)
    # and keep compatibility with old behavior where plain titles are passed.
    parsed = urlparse(raw_url)
    if parsed.path.startswith("/wiki/"):
        wiki_title = parsed.path.split("/wiki/", 1)[1]
    else:
        wiki_title = raw_url.split("/")[-1]

    wiki_title = unquote(wiki_title).strip()
    if wiki_title == "" or wiki_title.lower() in ["none", "null"]:
        return kno_title, kno_image

    if user_settings.javascript == "enabled":
        kno_title = f"/wikipedia?q={quote(wiki_title)}"
    else:
        try:
            user_agent = random.choice(user_agents)
            response = s.get(
                f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={quote(wiki_title)}&pithumbsize=500",
                headers={"User-Agent": user_agent},
                timeout=15,
            )
            data = json.loads(response.text)
            page_ids = list(data.get("query", {}).get("pages", {}).keys())
            if len(page_ids) > 0:
                page = data["query"]["pages"][page_ids[0]]
                thumb_src = page.get("thumbnail", {}).get("source")
                if thumb_src:
                    kno_image = f"/img_proxy?url={thumb_src}"
        except Exception:
            kno_image = None

    return kno_title, kno_image


def format_araa_name(json_obj):
    # Recursively format araa_name=ARAA_NAME
    if isinstance(json_obj, dict):
        return {key: format_araa_name(value) for key, value in json_obj.items()}
    elif isinstance(json_obj, list):
        return [format_araa_name(item) for item in json_obj]
    elif isinstance(json_obj, str):
        return json_obj.format(araa_name=ARAA_NAME)
    else:
        return json_obj
