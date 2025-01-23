ARAA_NAME = "Araa"

# The char used to denote bangs (see below).
# EG BANG='!': "!ddg cats" will search "cats" on DuckDuckGo.
BANG = '!'

# Search engine bangs for ppl who want to use another engine through
# Araa's search bar.
# Bangs with their assosiated URLs can be found in /bangs.json.

# The repository this instance is based off on.
REPO = 'https://github.com/Extravi/araa-search'
DONATE = 'https://github.com/sponsors/Extravi'

DEFAULT_ENGINE = "google"


# Default theme
DEFAULT_THEME = 'dark_default'

# Default method
DEFAULT_METHOD = "GET"

# Default autocomplete "google" will use Google, and "ddg" will use DuckDuckGo
DEFAULT_AUTOCOMPLETE = "google"

# The port for this server to listen on
PORT = 8000

# Torrent domains
TORRENTGALAXY_DOMAIN = "torrentgalaxy.to"
NYAA_DOMAIN = "nyaa.si"
# apibay is the api for thepiratebay.org
API_BAY_DOMAIN = "apibay.org"
RUTOR_DOMAIN = "rutor.info"

# Domain of the Piped instance to use
PIPED_INSTANCE_API = "ytapi.ttj.dev"
PIPED_INSTANCE = "yt.ttj.dev"
PIPED_INSTANCE_PROXY = "ytproxy.ttj.dev"

# Useragents to use in the request.
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.89",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
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
    "wikipedia.org",
    PIPED_INSTANCE,
    PIPED_INSTANCE_API,
    PIPED_INSTANCE_PROXY,
    "api.qwant.com",
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

UX_LANGUAGES = [
    {'lang_lower': 'english', 'lang_fancy': 'English'},
    {'lang_lower': 'danish', 'lang_fancy': 'Danish (Dansk)'},
    {'lang_lower': 'dutch', 'lang_fancy': 'Dutch (Nederlands)'},
    {'lang_lower': 'french', 'lang_fancy': 'French (Français)'},
    {'lang_lower': 'french_canadian', 'lang_fancy': 'French Canadian (Français canadien)'},
    {'lang_lower': 'german', 'lang_fancy': 'German (Deutsch)'},
    {'lang_lower': 'greek', 'lang_fancy': 'Greek (Ελληνικά)'},
    {'lang_lower': 'italian', 'lang_fancy': 'Italian (Italiano)'},
    {'lang_lower': 'japanese', 'lang_fancy': 'Japanese (日本語)'},
    {'lang_lower': 'korean', 'lang_fancy': 'Korean (한국어)'},
    {'lang_lower': 'mandarin_chinese', 'lang_fancy': 'Mandarin Chinese (普通话 or 中文)'},
    {'lang_lower': 'norwegian', 'lang_fancy': 'Norwegian (Norsk)'},
    {'lang_lower': 'polish', 'lang_fancy': 'Polish (Polski)'},
    {'lang_lower': 'portuguese', 'lang_fancy': 'Portuguese (Português)'},
    {'lang_lower': 'russian', 'lang_fancy': 'Russian (Русский)'},
    {'lang_lower': 'spanish', 'lang_fancy': 'Spanish (Español)'},
    {'lang_lower': 'swedish', 'lang_fancy': 'Swedish (Svenska)'},
    {'lang_lower': 'turkish', 'lang_fancy': 'Turkish (Türkçe)'},
    {'lang_lower': 'ukrainian', 'lang_fancy': 'Ukrainian (Українська)'},
    {'lang_lower': 'romanian', 'lang_fancy': 'Romanian (Română)'},
]

# See all the 'lang_lower' values in UX_LANGUAGES
DEFAULT_UX_LANG = "english"

DEFAULT_GOOGLE_DOMAIN = "/search?gl=us"

ENGINE_RATELIMIT_COOLDOWN_MINUTES = 28
