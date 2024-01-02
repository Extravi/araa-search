from src import helpers
from flask import request, jsonify
from urllib.parse import quote


def search(settings):
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    query = args.get("q", "")
    search_type = args.get("t", "text")
    p = args.get("p", 0)

    # search query
    if search_type == "reddit":
        site_restriction = "site:reddit.com"
        query_for_request = f"{query} {site_restriction}"
        soup = helpers.makeHTMLRequest(
            f"https://www.{settings.domain}&q={quote(query_for_request)}&start={p}&lr={settings.lang}"
        )
    elif search_type == "text":
        soup = helpers.makeHTMLRequest(f"https://www.{settings.domain}&q={quote(query)}&start={p}&lr={settings.lang}&safe={settings.safe}")
    else:
        return "Invalid search type"

    results_object = {}

    # Get all of the standard results.
    results = []
    title_divs = soup.findAll("div", {"class": "yuRUbf"})
    desc_divs = soup.findAll("div", {"class": "VwiC3b"})
    for result_iterator in range(len(desc_divs)):
        title_div = title_divs[result_iterator]
        results.append({
            "href": title_div.find("a").get("href", ""),
            "title": title_div.find("h3").text.strip(),
            "desc": desc_divs[result_iterator].text.strip(),
            "has_sublinks": False,
            "sublinks": []
        })

    # retrieve sublinks
    result_sublinks = soup.findAll("tr", {"class": lambda x: x and x.startswith("mslg")})
    sublinks = []
    for sublink in result_sublinks:
        link = sublink.find("a")
        try:
            sublinks.append({
                "desc": sublink.find("div", {"class": "zz3gNc"}).text.strip(),
                "href": link.get("href", ""),
                "title": link.text.strip()
            })
        except AttributeError:
            continue

    # retrieve featured snippet
    featured_snip = soup.find("span", {"class": "hgKElc"})
    if featured_snip is None:
        snip = ""
    else:
        snip = featured_snip.text.strip()

    # retrieve spell check
    try:
        spell = soup.find("a", {"class": "gL9Hy"})
        check = spell.text.strip().replace("site:reddit.com", "")
    except AttributeError:
        check = ""

    # Add the sublinks to the first element.
    if sublinks != []:
        results[0]['has_sublinks'] = True
        results[0]['sublinks'] = sublinks

    results_object = {
        "results": results,
        "snip": snip,
        "check": check,
        "wiki": wikipedia_answer(soup)
    }

    return results_object


def wikipedia_answer(soup):

    image = soup.find("g-img")
    if image is not None:
        image = image.get("data-lpage", "")
    else:
        image = ""

    # retrieve kno-rdesc
    try:
        rdesc = soup.find("div", {"class": "kno-rdesc"})
        span_element = rdesc.find("span")
        description = span_element.text
        wiki_link = rdesc.find("a").get("href")
    except AttributeError:
        return {
            "has_wiki": False
        }

    # retrieve kno-title
    try:  # look for the title inside of a span in div.SPZz6b
        rtitle = soup.find("div", {"class": "SPZz6b"})
        rt_span = rtitle.find("span")
        rkno_title = rt_span.text.strip()
        # if we didn't find anyhing useful, move to next tests
        if rkno_title in ["", "See results about"]:
            raise
    except:
        for element, class_name in zip(["div", "span", "div"], ["DoxwDb", "yKMVIe", "DoxwDb"]):
            try:
                rtitle = soup.find(element, {"class": class_name})
                rkno_title = rtitle.text.strip()
            except AttributeError:
                continue  # couldn't scrape anything. continue if we can.
            else:
                if rkno_title not in ["", "See results about"]:
                    break  # we got one
        else:
            rkno_title = ""

    if image != "":
        image = f"/img_proxy?url={image}",
    else:
        image = ""

    return {
        "has_wiki": True,
        "title": rkno_title,
        "description": description,
        "image": image,
        "link": wiki_link
    }
