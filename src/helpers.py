import random
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote
from _config import *
from markupsafe import escape, Markup
from os.path import exists
from langdetect import detect
from thefuzz import fuzz


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

# search highlights
def highlight_query_words(string, query):
    # detect the language of the string
    try:
        detected_language = detect(string)
    except:
        detected_language = ""
    string = escape(string)

    if detected_language in ['ja', 'zh', 'ko']:
        query_words = [re.escape(word) for word in query.lower().split()]
        query_regex = re.compile('|'.join(query_words), re.I)
        highlighted = query_regex.sub(lambda match: Markup(f'<span class="highlight">{match.group(0)}</span>'), string)
    else:
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


def makeJSONRequest(url: str):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab json content
    response = requests.get(url)

    # Return the JSON object
    return json.loads(response.text)

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
