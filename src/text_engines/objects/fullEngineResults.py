from src.text_engines.objects.textResult import TextResult
from dataclasses import dataclass

@dataclass
class FullEngineResults:
    engine: str
    search_type: str
    ok: bool
    code: int
    results: list[TextResult] | None = None,
    wiki: dict | None = None
    featured: str | None = None
    correction: str | None = None
    top_result_sublinks: str | None = None

    def asDICT(self):
        results_asdict = []

        for result in self.results:
            results_asdict.append(result.asDICT())

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
            "sublinks.len": len(self.top_result_sublinks),
        }