from dataclasses import dataclass, field

@dataclass
class WikiSnippet:
    title: str
    desc: str
    link: str
    image: str | None = None
    wiki_thumb_proxy_link: str | None = None
    known_for: str | None = None
    info: dict = field(default_factory = dict)

    def asDICT(self):
        # self.info is a dict[str, Tag] => `Tag`s are used because of links.
        # we just want a dict[str, str] => we don't want to perserve links, just text.
        info_cleaned = {}
        for info in self.info.items():
            keypoint = info[0][:len(info[0]) - 2] # remove a trailing ": "
            info_cleaned[keypoint] = info[1].get_text()

        return {
            "title": self.title,
            "image": self.image,
            "desc": self.desc,
            "link": self.link,
            "wiki_thumb_proxy_link": self.wiki_thumb_proxy_link,
            "known_for": self.known_for,
            "info": info_cleaned,
        }
