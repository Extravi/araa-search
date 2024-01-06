import random
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from _config import *
from markupsafe import escape, Markup
from os.path import exists
from langdetect import detect
from thefuzz import fuzz
from flask import request
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from twocaptcha import TwoCaptcha
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


# Force all requests to only use IPv4
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# Make persistent request sessions
s = requests.Session() # generic
google = requests.Session() # google
wiki = requests.Session() # wikipedia
invidious = requests.Session() # invidious

def makeHTMLRequest(url: str, is_google=False, is_wiki=False, is_invidious=False):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    if is_google:
        # get google cookies
        data = load_config()
        cookies = {
            "OGPC": data["GOOGLE_OGPC_COOKIE"],
            "NID": data["GOOGLE_NID_COOKIE"],
            "AEC": data["GOOGLE_AEC_COOKIE"],
            "1P_JAR": data["GOOGLE_1P_JAR_COOKIE"],
            "GOOGLE_ABUSE_EXEMPTION": data["GOOGLE_ABUSE_COOKIE"]
        }
    else:
        cookies = {}

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
        html = google.get(url, headers=headers, cookies=cookies) # persistent session for google
    elif is_wiki:
        html = wiki.get(url, headers=headers, cookies=cookies) # persistent session for wikipedia
    elif is_invidious:
        html = invidious.get(url, headers=headers, cookies=cookies) # persistent session for invidious
    else:
        html = s.get(url, headers=headers, cookies=cookies) # generic persistent session

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

def load_config():
    with open("./2captcha.json", "r") as file:
        return json.load(file)

def save_config(data):
    with open("./2captcha.json", "w") as file:
        json.dump(data, file, indent=4)

def captcha():
    # get google cookies
    data = load_config()
    CAPTCHA_SOLVER_ACTIVE = data["CAPTCHA_SOLVER_ACTIVE"]
    # check if solver is already running
    if CAPTCHA_SOLVER_ACTIVE == "false":
        # start solver
        data = load_config()
        data["CAPTCHA_SOLVER_ACTIVE"] = "true"
        save_config(data)
        solver = TwoCaptcha(CAPTCHA_API_KEY)

        # Choose a user-agent at random
        user_agent = random.choice(user_agents)
        headers = {"User-Agent": user_agent}

        # start the webdriver to use later
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        # url for captcha
        url = f"https://www.google.com/search?q="

        # Grab HTML content
        html = google.get(url, headers=headers) # use the persistent session for google
        url = html.url

        # get data-s tag
        soup = BeautifulSoup(html.text, "lxml")
        captcha_form = soup.find("form", {"id": "captcha-form"})
        recaptcha_div = captcha_form.find("div", {"class": "g-recaptcha"})
        data_s_value = recaptcha_div.get("data-s", "")

        # try to solve captcha
        try:
            result = solver.recaptcha(
            sitekey="6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b",
            datas=f"{data_s_value}",
            url=f"{url}")
        except Exception as e:
            data = load_config()
            data["CAPTCHA_SOLVER_ACTIVE"] = "false"
            save_config(data) 
            driver.close()
            print(e)
        else:
            # get the captcha code
            code = result['code']
            # request the page
            driver.get(url)
            # set the solved code
            while True:
                # Sometimes Google won't load the captcha even on a fully loaded page, so refresh until it's loaded.
                try:
                    recaptcha_response_element = driver.find_element(By.ID, 'g-recaptcha-response')
                    break 
                except NoSuchElementException:
                    driver.refresh()
            driver.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)
            # continue and get cookies
            continue_input = driver.find_element(By.CSS_SELECTOR, 'form#captcha-form input[name="continue"]')
            continue_input.submit()
            # capture cookie value to send in request
            cookies = driver.get_cookies()
            data = load_config()
            for cookie in cookies:
                cookie_name = cookie['name']
                if cookie_name in cookie_mapping:
                    data[cookie_mapping[cookie_name]] = cookie['value']
            save_config(data)
            # close the web driver and set solver to false
            data = load_config()
            data["CAPTCHA_SOLVER_ACTIVE"] = "false"
            save_config(data)
            driver.close()
    else:
        pass

def makeJSONRequest(url: str):
    # block unwanted request from an edited cookie
    domain = unquote(url).split('/')[2]
    if domain not in WHITELISTED_DOMAINS:
        raise Exception(f"The domain '{domain}' is not whitelisted.")

    # Choose a user-agent at random
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    # Grab json content
    response = s.get(url)

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

class Settings():
    def __init__(self):
        self.domain = request.cookies.get("domain", "/search?gl=us")
        self.javascript = request.cookies.get("javascript", "enabled")
        self.lang = request.cookies.get("lang", "")
        self.new_tab = request.cookies.get("new_tab", "")
        self.safe = request.cookies.get("safe", "active")
        self.ux_lang = request.cookies.get("ux_lang", "english")
        self.theme = request.cookies.get("theme", DEFAULT_THEME)
        self.method = request.cookies.get("method", DEFAULT_METHOD)
        self.ac = request.cookies.get("ac", DEFAULT_AUTOCOMPLETE)
