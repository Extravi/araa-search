from src import helpers
from urllib.parse import unquote
from _config import *
from src.text_engines.objects.fullEngineResults import FullEngineResults
from src.text_engines.objects.textResult import TextResult
from flask import request
import requests


NAME = "google"


def _extract_correction(payload: dict):
    check = ""

    if not LOCAL_SEARXNG_GOOGLE_ENABLE_CORRECTIONS:
        return check

    # prefer native correction field when available
    try:
        spell = payload.get("corrections", [])[0]
        check = str(spell).strip()
    except Exception:
        check = ""

    # optional fallback for engines that only emit suggestions
    if check == "" and LOCAL_SEARXNG_GOOGLE_USE_SUGGESTIONS_FALLBACK:
        try:
            spell = payload.get("suggestions", [])[0]
            check = str(spell).strip()
        except Exception:
            check = ""

    return check


def search(query: str, page: int, search_type: str, user_settings: helpers.Settings) -> FullEngineResults:
    original_query = query

    if search_type == "reddit":
        query += " site:reddit.com"

    after_date = request.args.get("after", "")
    before_date = request.args.get("before", "")
    if after_date != "":
        query += f" after:{after_date}"
    if before_date != "":
        query += f" before:{before_date}"

    # Query the local searxng instance configured during server startup.
    # This keeps google scraping logic out of Araa itself.
    page_offset = helpers._safe_int(page, 0)
    if page_offset < 0:
        page_offset = 0

    # Araa paging uses offsets (0, 10, 20...). SearXNG expects page numbers (1, 2, 3...).
    page_num = (page_offset // 10) + 1

    try_knowledge_panel = helpers.should_request_knowledge_panel(original_query, search_type, page_num)

    engines = ["google"]
    if try_knowledge_panel:
        engines.append("wikipedia")

    safesearch = 1 if user_settings.safe == "active" else 0
    link_args = {
        "q": query,
        "format": "json",
        "engines": ",".join(engines),
        "safesearch": safesearch,
        "pageno": page_num,
    }

    searx_lang = helpers.settings_lang_to_searx(user_settings.lang)
    if searx_lang != "":
        link_args["language"] = searx_lang

    link = f"{helpers._local_searxng_base_url()}/search"

    try:
        response = requests.get(link, params=link_args, timeout=45)
    except Exception:
        return FullEngineResults(engine="google", search_type=search_type, ok=False, code=503)

    response_code = response.status_code
    if response_code != 200:
        return FullEngineResults(engine="google", search_type=search_type, ok=False, code=response_code)

    try:
        payload = response.json()
    except Exception:
        return FullEngineResults(engine="google", search_type=search_type, ok=False, code=response_code)

    if not isinstance(payload, dict):
        return FullEngineResults(engine="google", search_type=search_type, ok=False, code=response_code)

    # retrieve search results
    results = []
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue

        href = str(result.get("url", "")).strip()
        title = str(result.get("title", "")).strip()
        desc = str(result.get("content", "")).strip()

        results.append(TextResult(
            url=unquote(href),
            title=title,
            desc=desc,
            sublinks=[]
        ))

    # retrieve featured snippet
    try:
        featured_snip = payload.get("answers", [])[0]
        snip = str(featured_snip).strip()
    except Exception:
        snip = ""

    # retrieve spell check / suggestion
    check = _extract_correction(payload)

    if search_type == "reddit":
        check = check.replace("site:reddit.com", "").strip()

    # retrieve wiki snippet
    wiki = helpers.build_wiki_snippet(payload, user_settings, allow_result_fallback=try_knowledge_panel)

    return FullEngineResults(
        engine="google",
        search_type=search_type,
        ok=True,
        code=200,
        results=results,
        wiki=wiki,
        featured=None if snip == "" else snip,
        correction=None if check == "" else check,
        top_result_sublinks=[],
    )
