from src import helpers
from urllib.parse import unquote, urlparse, parse_qs, urlencode
from _config import *
from src.text_engines.objects.fullEngineResults import FullEngineResults
from src.text_engines.objects.wikiSnippet import WikiSnippet
from src.text_engines.objects.textResult import TextResult
from flask import request


NAME = "google"


def __local_href__(url):
    url_parsed = parse_qs(urlparse(url).query)
    if "q" not in url_parsed:
        return ""
    return f"/search?q={url_parsed['q'][0]}&p=0&t=text"


def search(query: str, page: int, search_type: str, user_settings: helpers.Settings) -> FullEngineResults:
    if search_type == "reddit":
        query += " site:reddit.com"

    after_date = request.args.get("after", "")
    before_date = request.args.get("before", "")
    if after_date != "":
        query += f" after:{after_date}"
    if before_date != "":
        query += f" before:{before_date}"

    # Random characters are to trick google into thinking it's a mobile phone
    # loading more results
    # -> https://github.com/searxng/searxng/issues/159
    link_args = {
        "q": query,
        "start": page,
        "lr": user_settings.lang,
        "num": 20,
        "safe": user_settings.safe,
        "vet": "12ahUKEwjE4O6xoajxAhWL_KQKHVCLBKoQxK8CegQIAhAG..i",
        "ved": "2ahUKEwjE4O6xoajxAhWL_KQKHVCLBKoQqq4CegQIAhAI",
        "yv": 3,
        "prmd": "vmin",
        "ei": "c0fQYITbBIv5kwXQlpLQCg",
        "sa": "N",
        "asearch": "arc",
        "async": "arc_id:srp_510,ffilt:all,ve_name:MoreResultsContainer,next_id:srp_5,use_ac:true,_id:arc-srp_510,_pms:qs,_fmt:pc"
    }
    link = f"https://www.google.com{user_settings.domain}&" + urlencode(link_args)

    soup, response_code = helpers.makeHTMLRequest(link, is_google=True)

    if response_code != 200:
        return FullEngineResults(engine="google", search_type=search_type, ok=False, code=response_code)

    # retrieve links
    result_divs = soup.findAll("div", {"class": "yuRUbf"})
    links = [div.find("a") for div in result_divs]
    hrefs = [link.get("href") for link in links]

    # retrieve title
    h3 = [div.find("h3") for div in result_divs]
    titles = [titles.text.strip() for titles in h3]

    # retrieve description
    result_desc = soup.findAll("div", {"class": "VwiC3b"})
    descriptions = [descs.text.strip() for descs in result_desc]

    # retrieve sublinks
    try:
        result_sublinks = soup.findAll("tr", {"class": lambda x: x and x.startswith("mslg")})
        sublinks_divs = [sublink.find("div", {"class": "zz3gNc"}) for sublink in result_sublinks]
        sublinks = [sublink.text.strip() for sublink in sublinks_divs]
        sublinks_links = [sublink.find("a") for sublink in result_sublinks]
        sublinks_hrefs = [link.get("href") for link in sublinks_links]
        sublinks_titles = [title.text.strip() for title in sublinks_links]
    except:
        sublinks = ""
        sublinks_hrefs = ""
        sublinks_titles = ""

    # retrieve kno-rdesc
    try:
        rdesc = soup.find("div", {"class": "CYJS5e"})
        span_element = rdesc.find("span", {"class": "QoPDcf"})
        desc_link = rdesc.find("a", {"class": "y171A"})
        kno_link = desc_link.get("href")
        kno = span_element.find("span").get_text()
    except:
        kno = ""
        kno_link = ""

    # retrieve kno-title
    try:  # look for the title inside of a span in div.SPZz6b
        rtitle = soup.find("div", {"class": "SPZz6b"})
        rt_span = rtitle.find("span")
        rkno_title = rt_span.text.strip()
        # if we didn't find anyhing useful, move to next tests
        if rkno_title in ["", "See results about"]:
            raise
    except:
        for ellement, class_name in zip(["div", "span", "div"], ["DoxwDb", "yKMVIe", "DoxwDb"]):
            try:
                rtitle = soup.find(ellement, {"class": class_name})
                rkno_title = rtitle.text.strip()
            except:
                continue  # couldn't scrape anything. continue if we can.
            else:
                if rkno_title not in ["", "See results about"]:
                    break  # we got one
        else:
            rkno_title = ""

    for div in soup.find_all("div", {'class': 'nnFGuf'}): 
        div.decompose()

    # retrieve featured snippet
    try:
        featured_snip = soup.find("span", {"class": "hgKElc"})
        snip = featured_snip.text.strip()
    except:
        snip = ""

    # retrieve spell check
    try:
        spell = soup.find("a", {"class": "gL9Hy"})
        check = spell.text.strip()
    except:
        check = ""
    if search_type == "reddit":
        check = check.replace("site:reddit.com", "").strip()

    kno_image = None
    kno_title = None

    # get wiki image
    if kno_link != "":
        kno_title, kno_image = helpers.grab_wiki_image_from_url(kno_link, user_settings)

    wiki_known_for = soup.find("div", {'class': 'loJjTe'})
    if wiki_known_for is not None:
        wiki_known_for = wiki_known_for.get_text().strip()

    wiki_info = {}
    wiki_info_divs = soup.find_all("div", {"class": "rVusze"})
    for info in wiki_info_divs:
        spans = info.findChildren("span" , recursive=False)
        for a in spans[1].find_all("a"):
            # Delete all non-href attributes
            a.attrs = {"href": a.get("href", "")}
            if "sca_esv=" in a['href']:
                # Remove any trackers for google domains
                a['href'] = __local_href__(a.get("href", ""))

        wiki_info[spans[0].get_text()] = spans[1]

    results = []
    for href, title, desc in zip(hrefs, titles, descriptions):
        results.append(TextResult(
            url = unquote(href),
            title = title,
            desc = desc,
            sublinks=[]
        ))
    sublink = []
    for sublink_href, sublink_title, sublink_desc in zip(sublinks_hrefs, sublinks_titles, sublinks):
        sublink.append(TextResult(
            url = unquote(sublink_href),
            title = sublink_title,
            desc = sublink_desc,
            sublinks=[]
        ))

    wiki = None if kno == "" else WikiSnippet(
        title = rkno_title,
        image = kno_image,
        desc = kno,
        link = unquote(kno_link),
        wiki_thumb_proxy_link = kno_title,
        known_for = wiki_known_for,
        info = wiki_info,
    )

    return FullEngineResults(
        engine = "google",
        search_type = search_type,
        ok = True,
        code = 200,
        results = results,
        wiki = wiki,
        featured = None if snip == "" else snip,
        correction = None if check == "" else check,
        top_result_sublinks = sublink,
    )
