from bs4 import BeautifulSoup
from urllib.parse import unquote
import random
from _config import *
from flask import escape, Markup
import requests
import re
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
    highlighted_words = []
    for word in words:
        cleaned_word = word.strip()
        if any(re.search(query_word, cleaned_word, re.IGNORECASE) for query_word in query_words):
            highlighted_word = re.sub('|'.join(query_words), lambda m: f'<span class="highlight">{escape(m.group())}</span>', cleaned_word, flags=re.IGNORECASE)
            highlighted_words.append(highlighted_word)
        else:
            highlighted_words.append(escape(word))
    return Markup(' '.join(highlighted_words))


def latest_commit():
    if exists(".git/refs/heads/main"):
        with open('./.git/refs/heads/main') as f:
            return f.readline()
    return "Not in main branch"
