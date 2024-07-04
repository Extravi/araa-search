from src.text_engines.objects.textResult import TextResult
from src.text_engines.objects.wikiSnippet import WikiSnippet
from dataclasses import dataclass

@dataclass
class FullEngineResults:
    engine: str
    search_type: str
    ok: bool
    code: int
    results: list[TextResult] | None = None
    wiki: WikiSnippet | None = None
    featured: str | None = None
    correction: str | None = None
    top_result_sublinks: list[TextResult] | None = None

    def asDICT(self):
        results_asdict = []

        for result in self.results:
            results_asdict.append(result.asDICT())

        ret = {
            "engine": self.engine,
            "type": self.search_type,
            "ok": self.ok,
            "code": self.code,
            "results": results_asdict,
            "wiki": self.wiki.asDICT() if self.wiki != None else None,
            "featured": self.featured,
            "correction": self.correction,
            "sublinks": self.top_result_sublinks,
        }

        if ret["results"] is not None:
            ret["results.len"] = len(results_asdict),
        if ret["sublinks"] is not None:
            ret["sublinks.len"] = len(self.top_result_sublinks)

        return ret
