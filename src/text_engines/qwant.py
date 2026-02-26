from src import helpers
from urllib.parse import unquote
from _config import *
from src.text_engines.objects.fullEngineResults import FullEngineResults
from src.text_engines.objects.wikiSnippet import WikiSnippet
from src.text_engines.objects.textResult import TextResult
from flask import request
import requests
import os


NAME = "qwant"


def _safe_int(value, fallback=0):
    try:
        return int(value)
    except Exception:
        return fallback


def _local_searxng_base_url():
    # Prefer the URL exposed by startup bootstrap logic.
    base_url = os.environ.get("ARAA_LOCAL_SEARXNG_URL", "").strip()
    if base_url != "":
        return base_url.rstrip("/")

    # Fallback to static config if the bootstrap did not set env vars.
    return f"http://{LOCAL_SEARXNG_HOST}:{LOCAL_SEARXNG_PORT}"


def _build_wiki_snippet(payload: dict, user_settings: helpers.Settings, allow_result_fallback: bool = False):
    def _normalize_url(raw_url):
        url = str(raw_url or "").strip()
        if url.lower() in ["none", "null"]:
            return ""
        return url

    def _first_wikipedia_url():
        for result in payload.get("results", []):
            if not isinstance(result, dict):
                continue
            candidate = _normalize_url(result.get("url", ""))
            if "wikipedia.org/wiki/" in candidate.lower():
                return candidate
        return ""

    infoboxes = payload.get("infoboxes", [])
    infobox = None
    if isinstance(infoboxes, list):
        infobox = next((entry for entry in infoboxes if isinstance(entry, dict)), None)

    if infobox is not None:
        title = str(infobox.get("infobox", "") or infobox.get("title", "")).strip()
        desc = str(infobox.get("content", "")).strip()
        link = _normalize_url(infobox.get("url", ""))
        if link == "" and allow_result_fallback:
            link = _first_wikipedia_url()

        if title != "" or desc != "":
            wiki_proxy_link = None
            wiki_image = None
            if link != "":
                wiki_proxy_link, wiki_image = helpers.grab_wiki_image_from_url(link, user_settings)

            return WikiSnippet(
                title=title,
                image=wiki_image,
                desc=desc,
                link=unquote(link),
                wiki_thumb_proxy_link=wiki_proxy_link,
                info={},
            )

    if not allow_result_fallback:
        return None

    # Fallback: build a panel from the first wikipedia result if infoboxes
    # are not returned by local searxng for this query.
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue

        link = _normalize_url(result.get("url", ""))
        if "wikipedia.org/wiki/" not in link.lower():
            continue

        title = str(result.get("title", "")).strip()
        desc = str(result.get("content", "")).strip()
        if title == "" and desc == "":
            continue

        wiki_proxy_link = None
        wiki_image = None
        if link != "":
            wiki_proxy_link, wiki_image = helpers.grab_wiki_image_from_url(link, user_settings)

        return WikiSnippet(
            title=title,
            image=wiki_image,
            desc=desc,
            link=unquote(link),
            wiki_thumb_proxy_link=wiki_proxy_link,
            info={},
        )

    return None


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

    page_offset = _safe_int(page, 0)
    if page_offset < 0:
        page_offset = 0

    # Araa paging uses offsets (0, 10, 20...). SearXNG expects page numbers (1, 2, 3...).
    page_num = (page_offset // 10) + 1

    try_knowledge_panel = helpers.should_request_knowledge_panel(original_query, search_type, page_num)

    engines = ["qwant"]
    if try_knowledge_panel:
        engines.append("wikipedia")

    link_args = {
        "q": query,
        "format": "json",
        "engines": ",".join(engines),
        "safesearch": 2 if user_settings.safe == "active" else 0,
        "pageno": page_num,
    }

    searx_lang = helpers.settings_lang_to_searx(user_settings.lang)
    if searx_lang != "":
        link_args["language"] = searx_lang

    link = f"{_local_searxng_base_url()}/search"

    try:
        response = requests.get(link, params=link_args, timeout=45)
    except Exception:
        return FullEngineResults(engine="qwant", search_type=search_type, ok=False, code=503)

    response_code = response.status_code
    if response_code != 200:
        return FullEngineResults(engine="qwant", search_type=search_type, ok=False, code=response_code)

    try:
        payload = response.json()
    except Exception:
        return FullEngineResults(engine="qwant", search_type=search_type, ok=False, code=response_code)

    if not isinstance(payload, dict):
        return FullEngineResults(engine="qwant", search_type=search_type, ok=False, code=response_code)

    # retrieve search results
    results = []
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue

        href = str(result.get("url", "")).strip()
        title = str(result.get("title", "")).strip()
        desc = str(result.get("content", "")).strip()

        results.append(TextResult(
            title=title,
            desc=desc,
            url=unquote(href),
            sublinks=[]
        ))

    # retrieve featured snippet
    try:
        featured_snip = payload.get("answers", [])[0]
        snip = str(featured_snip).strip()
    except Exception:
        snip = ""

    # retrieve spell check
    try:
        spell = payload.get("corrections", [])[0]
        check = str(spell).strip()
    except Exception:
        check = ""

    if search_type == "reddit":
        check = check.replace("site:reddit.com", "").strip()

    # retrieve wiki snippet
    wiki = _build_wiki_snippet(payload, user_settings, allow_result_fallback=try_knowledge_panel)

    return FullEngineResults(
        engine="qwant",
        search_type=search_type,
        ok=True,
        code=200,
        results=results,
        wiki=wiki,
        featured=None if snip == "" else snip,
        correction=None if check == "" else check,
        top_result_sublinks=[],
    )
