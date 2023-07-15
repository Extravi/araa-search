# The char used to denote bangs (see below).
# EG BANG='!': "!ddg cats" will search "cats" on DuckDuckGo.
BANG = '!'

# Search engine bangs for ppl who want to use another engine through
# TailsX's search bar.
# Bangs with their assosiated URLs can be found in /bangs.json.

# The repository this instance is based off on.
REPO='https://github.com/Extravi/tailsx'

# Default theme
DEFAULT_THEME = 'dark_blur'

# The port for this server to listen on
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

# prompts for user agent & ip queries
VALID_IP_PROMPTS = [
    "what is my ip",
    "what is my ip address",
    "what's my ip",
    "whats my ip"
]
VALID_UA_PROMPTS = [
    "what is my user agent",
    "what is my useragent",
    "whats my useragent",
    "whats my user agent",
    "what's my useragent",
    "what's my user agent",
]


WHITELISTED_DOMAINS = [
    "www.google.com",
    "www.google.fr",
    "www.google.ca",
    "www.google.co.uk",
    "www.google.de",
    "www.google.com.au",
    "www.google.co.in",
    "www.google.co.jp",
    "www.google.co.kr",
    "www.google.com.br",
    "wikipedia.org",
    "yt.revvy.de",
    "lite.qwant.com"
]

COOKIE_AGE = 2147483647


# if you are using a custom Invidious you have to add it to the whitelist above
INVIDIOUS_INSTANCE = "yt.revvy.de"
