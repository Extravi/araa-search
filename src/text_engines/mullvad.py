from src import helpers
from urllib.parse import unquote, urlparse, parse_qs, urlencode
from _config import *
from src.text_engines.objects.fullEngineResults import FullEngineResults
from src.text_engines.objects.wikiSnippet import WikiSnippet
from src.text_engines.objects.textResult import TextResult
from flask import request

NAME = "mullvad"

def search(query: str, page: int, search_type: str, user_settings: helpers.Settings) -> FullEngineResults:
    # Mullvad expects an `engine` parameter indicating the search backend
    # We always send `engine=google` to match the other engine-based implementations
    link_args = {
        "q": query,
        "engine": "google"
    }
    link = f"https://leta.mullvad.net/search/__data.json?" + urlencode(link_args)

    # print the url for debugging
    print(f"[mullvad.py] Requesting URL: {link}")

    # Mullvad returns JSON at this endpoint. Use the JSON helper which also
    # enforces domain whitelisting.
    soup, response_code = helpers.makeJSONRequest(link)

    if response_code != 200 or soup is None:
        return FullEngineResults(engine="mullvad", search_type=search_type, ok=False, code=response_code)

    # Convert the Mullvad "nodes" format into a flat list of result dicts.
    output = []
    nodes = soup.get("nodes", []) if isinstance(soup, dict) else []
    for node in nodes:
        if node is None or node.get("type") != "data":
            continue
        node_data = node.get("data", [])
        if not isinstance(node_data, list) or len(node_data) < 1:
            continue
        # node_data[0] contains metadata, including the index of the `items` list
        meta = node_data[0] if isinstance(node_data[0], dict) else {}
        items_index = meta.get("items")
        if items_index is None or items_index >= len(node_data):
            continue
        result_pointers = node_data[items_index]
        if not isinstance(result_pointers, list):
            continue

        for pointer in result_pointers:
            if pointer is None or pointer >= len(node_data):
                continue
            start = node_data[pointer]
            if not isinstance(start, dict):
                continue
            result = {}
            for name, p2 in start.items():
                # guard index access
                try:
                    value = node_data[p2]
                except Exception:
                    value = None
                result[name] = value
            output.append(result)

    # Build TextResult objects from the parsed output
    results = []
    for item in output:
        # link, title, snippet, favicon
        url = item.get("link") or ""
        title = item.get("title") or ""
        snippet = item.get("snippet") or ""
        # Ensure values are strings
        try:
            url = unquote(url)
        except Exception:
            url = str(url)
        title = str(title)
        snippet = str(snippet)

        results.append(TextResult(
            url=url,
            title=title,
            desc=snippet,
            sublinks=[]
        ))

    return FullEngineResults(
        engine="mullvad",
        search_type=search_type,
        results=results,
        ok=True,
        code=200
    )