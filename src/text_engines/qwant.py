from src.text_engines.objects.fullEngineResults import FullEngineResults
from src.text_engines.objects.textResult import TextResult
from src.text_engines.objects.wikiSnippet import WikiSnippet
from urllib.parse import urlparse, urlencode, quote
from src import helpers

# NOTE: Qwant engine made by amongusussy. Taken from https://github.com/Extravi/araa-search/pull/106
# Slightly modified to adapt different text results engine.
def search(query: str, page: int, search_type: str, user_settings: helpers.Settings) -> FullEngineResults:
    if search_type == "reddit":
        query += " site:reddit.com"

    url_args = {
        "t": "web",
        "q": query,
        "count": 10,
        "locale": "en_us",
        "offset": page,
        "device": "desktop",
        "safesearch": 2 if user_settings.safe == "active" else 0,
        "tgp": 1,
    }

    json_data, code = helpers.makeJSONRequest("https://api.qwant.com/v3/search/web?{}".format(urlencode(url_args)))

    if code == 403 and user_settings.safe == "active":
        # Qwant returns 403 when safesearch restricted all content.
        # This is just to prevent an 'engine failure' error.
        return FullEngineResults(
            engine = "qwant",
            search_type = search_type,
            ok = True,
            code = code,
        )

    if json_data['status'] != "success":
        # Add error handling later
        return FullEngineResults(
            engine = "qwant",
            search_type = search_type,
            ok = False,
            code = code,
        )

    resp_results = json_data.get("data", {}).get("result", {}).get("items", {}).get("mainline")
    if resp_results is None:
        return FullEngineResults(
            engine = "qwant",
            search_type = search_type,
            ok = False,
            code = code,
        )

    web_results = []
    for group in resp_results:
        if group.get("type") == "web":
            # Only get web results. No images/ads.
            web_results += group.get("items", [])

    results = []
    wiki = None
    for result in web_results:
        if len(result['desc']) > 166:
            short_desc = result['desc'][:166] + "..."
        else:
            short_desc = result['desc']
        results.append(TextResult(
            title = result['title'],
            desc = short_desc,
            url = result['url'],
        ))

        # wikipedia snippet scraper
        if wiki is None and 'wikipedia.org' in urlparse(result['source']).netloc:
            wiki_proxy_link, wiki_image = helpers.grab_wiki_image_from_url(result['source'], user_settings)

            wiki = WikiSnippet(
                title = result['title'],
                desc = result['desc'],
                link = result['source'],
                image = wiki_image,
                wiki_thumb_proxy_link = wiki_proxy_link,
            )

    spell = json_data['data']['query']['queryContext'].get('alteredQuery', '')

    return FullEngineResults(
        engine = "qwant",
        search_type = search_type,
        ok = True,
        code = 200,
        results = results,
        wiki = wiki,
        correction = spell,
    )

