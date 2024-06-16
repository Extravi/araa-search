class TextEngineResults:
    def __init__(self, engine: str, search_type: str, ok: bool, code: int, results: list | None = None,
                 wiki: dict | None = None, featured: str | None = None, correction: str | None = None,
                 top_result_sublinks: str | None = None):
        self.engine = engine
        self.search_type = search_type
        self.ok = ok
        self.code = code
        self.results = results
        self.wiki = wiki
        self.featured = featured
        self.correction = correction
        self.top_result_sublinks = top_result_sublinks

    # Only made for debugging.
    def __str__(self):
        return f"""
engine       = {self.engine}
type         = {self.search_type}
ok           = {self.ok}
code         = {self.code}
results      = {self.results}
len(results) = {len(self.results)}
wiki         = {self.wiki}
featured     = {self.featured}
correction   = {self.correction}
sublinks     = {self.top_result_sublinks}
"""

    def __repr__(self):
        return self.__str__()

    # Technically a dict, but it works, so.
    def asDICT(self):
        return {
            "engine": self.engine,
            "type": self.search_type,
            "ok": self.ok,
            "code": self.code,
            "results": self.results,
            "results.len": len(self.results),
            "wiki": self.wiki,
            "featured": self.featured,
            "correction": self.correction,
            "sublinks": self.top_result_sublinks,
            "sublinks.len": len(self.top_result_sublinks),
        }
