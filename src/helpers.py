from bs4 import BeautifulSoup
from urllib.parse import unquote
import random
from _config import *
from markupsafe import escape, Markup
import requests
import re
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
    detected_language = detect(string)
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
