The file should be saved to a file in `static/lang/` and should be titled with the english name of the language in all lower case, followed by '.json'.

Make sure to add an entry to `UX_LANGUAGES` in _config.py

It should be formatted like this:

    {'lang_lower': 'french', 'lang_fancy': 'French (Français)'},

`lang_lower` should match the first part of the json file (e.g. 'english' for 'english.json').
`lang_fancy` should be the name of the language in english with the first letter capitalized, followed by the name of the language in its own language in brackets.
