from dataclasses import dataclass

# Provided as a 'blueprint' for a singular result from the text engine.
@dataclass
class TextResult:
    title: str
    desc: str
    url: str

    def asDICT(self):
        return {
            "title": self.title,
            "desc": self.desc,
            "url": self.url,
        }
