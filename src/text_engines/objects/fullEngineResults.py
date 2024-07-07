from src.text_engines.objects.textResult import TextResult
from src.text_engines.objects.wikiSnippet import WikiSnippet
from dataclasses import dataclass, field

@dataclass
class FullEngineResults:
    engine: str
    search_type: str
    ok: bool
    code: int
    results: list[TextResult] = field(default_factory = list)
    wiki: WikiSnippet | None = None
    featured: str | None = None
    correction: str | None = None
    top_result_sublinks: list[TextResult] = field(default_factory = list)

    def asDICT(self):
        results_asdict = [result.asDICT() for result in self.results]

        return {
            "engine": self.engine,
            "type": self.search_type,
            "ok": self.ok,
            "code": self.code,
            "results": results_asdict,
            "results.len": len(results_asdict),
            "wiki": self.wiki.asDICT() if self.wiki != None else None,
            "featured": self.featured,
            "correction": self.correction,
            "sublinks": self.top_result_sublinks,
            "sublinks.len": len(self.top_result_sublinks)
        }

