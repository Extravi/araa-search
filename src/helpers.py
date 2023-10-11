import random
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote
from _config import *
from markupsafe import escape, Markup
from os.path import exists


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
    query_words = [re.escape(word) for word in query.lower().split()]
    words = string.split()
    highlighted = []
    query_regex = re.compile('|'.join(query_words))
    highlighted_words = []
    for word in words:
        cleaned_word = word.strip().lower()
        escaped_word = escape(word)
        if query_regex.search(cleaned_word) and cleaned_word not in highlighted:
            highlighted_words.append(Markup(f'<span class="highlight">{escaped_word}</span>'))
            highlighted.append(cleaned_word)
        else:
            highlighted_words.append(escaped_word)
    return Markup(' '.join(highlighted_words))


def latest_commit():
    if exists(".git/refs/heads/main"):
        with open('./.git/refs/heads/main') as f:
            return f.readline()
    return "Not in main branch"


def makeHTMLRequest(url: str):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab HTML content
    response = requests.get(url)

    # Return the BeautifulSoup object
    return json.loads(response.content)
