Each engine (.py file) has a 'search' method, which takes in a query (string) and a page (int).

The search method must return a dictionary containing the following;

| Key | Type(s) | Description |
|-|-|-|
| `engine` | `str` | The engine used to perform the search |
| `type` | `str` | The type of search performed |
| `ok` | `bool` | Whether or not the search was successful |
| `results` | `list` \| `None` | A list containing results. See the spec for results elsewhere in this document. This may (and likely will) be None if `ok` is False. |
| `wiki` | `dict` \| `None` | A dictionary containing information important for the wiki snippet in text results. See the spec for this elsewhere in the document. This may be None if a wiki snippet cannot be formed. |
| `correction` |  |  |
| `snip` |  |  |
| `snipp` |  |  |
