from src import helpers
from urllib.parse import quote, unquote
from _config import *
from src.text_engines.textEngineResults import TextEngineResults

def __local_href__(url):
    url_parsed = parse_qs(urlparse(url).query)
    if "q" not in url_parsed:
        return ""
    return f"/search?q={url_parsed['q'][0]}&p=0&t=text"

def search(query: str, page: int, search_type: str, user_settings: helpers.Settings) -> TextEngineResults:
    if search_type == "reddit":
        query += " site:reddit.com"

    soup, response_code = helpers.makeHTMLRequest(f"https://www.google.com{user_settings.domain}&q={quote(query)}&start={page}&lr={user_settings.lang}&num=20", is_google=True)

    if response_code != 200:
        return TextEngineResults(engine="google", search_type=search_type, ok=False, code=response_code)

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
        rdesc = soup.find("div", {"class": "kno-rdesc"})
        span_element = rdesc.find("span")
        kno = span_element.text
        desc_link = rdesc.find("a")
        kno_link = desc_link.get("href")
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

    # get image for kno try javascript version first
    if user_settings.javascript == "enabled":
        if kno_link == "":
            kno_image = ""
            kno_title = ""
        else:
            kno_title = kno_link.split("/")[-1]
            kno_title = f"/wikipedia?q={kno_title}"
            kno_image = ""
    else:
        if kno_link == "":
            kno_image = ""
            kno_title = ""
        else:
            try:
                kno_title = kno_link.split("/")[-1]
                soup = makeHTMLRequest(f"https://wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={kno_title}&pithumbsize=500", is_wiki=True)
                data = json.loads(soup.text)
                img_src = data['query']['pages'][list(data['query']['pages'].keys())[0]]['thumbnail']['source']
                kno_image = [f"/img_proxy?url={img_src}"]
                kno_image = ''.join(kno_image)
            except:
                kno_image = ""

    wiki_known_for = soup.find("div", {'class': 'loJjTe'})
    if wiki_known_for is not None:
        wiki_known_for = wiki_known_for.get_text()

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

    # list
    results = []
    for href, title, desc in zip(hrefs, titles, descriptions):
        results.append({
            "url":   unquote(href),
            "title": title,
            "desc":  desc,
        })
    sublink = []
    for sublink_href, sublink_title, sublink_desc in zip(sublinks_hrefs, sublinks_titles, sublinks):
        sublink.append({
            "url":   unquote(sublink_href),
            "title": sublink_title,
            "desc":  sublink_desc,
        })

    wiki = None if kno == "" else {
        "title": rkno_title,
        "image": kno_image,
        "desc": kno,
        "link": unquote(kno_link),
        "wiki_thumb_proxy_link": kno_title,
    }

    return TextEngineResults(
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
