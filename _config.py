# The char used to denote bangs (see below).
# EG BANG='!': "!ddg cats" will search "cats" on DuckDuckGo.
BANG = '!'

# Search engine bangs for ppl who want to use another engine through
# Araa's search bar.
# Bangs with their assosiated URLs can be found in /bangs.json.

# The repository this instance is based off on.
REPO = 'https://github.com/Extravi/araa-search'

# Default theme
DEFAULT_THEME = 'dark_blur'

# The port for this server to listen on
PORT = 8000

# Torrent domains
TORRENTGALAXY_DOMAIN = "torrentgalaxy.to"
NYAA_DOMAIN = "nyaa.si"
# apibay is the api for thepiratebay.org
API_BAY_DOMAIN = "apibay.org"
RUTOR_DOMAIN = "rutor.info"

# Domain of the Invidious instance to use
INVIDIOUS_INSTANCE = "yt.artemislena.eu"

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
    INVIDIOUS_INSTANCE,
    "lite.qwant.com",
    TORRENTGALAXY_DOMAIN,
    NYAA_DOMAIN,
    API_BAY_DOMAIN,
    RUTOR_DOMAIN,
]

ENABLED_TORRENT_SITES = [
    "nyaa",
    "torrentgalaxy",
    "tpb",
    "rutor",
]

TORRENT_TRACKERS = [
    'http://nyaa.tracker.wf:7777/announce',
    'udp://open.stealth.si:80/announce',
    'udp://tracker.opentrackr.org:1337/announce',
    'udp://exodus.desync.com:6969/announce',
    'udp://tracker.torrent.eu.org:451/announce'
]

COOKIE_AGE = 2147483647

# set to true to enable api support
API_ENABLED = False

# set to false to disable torrent search
TORRENTSEARCH_ENABLED = True
