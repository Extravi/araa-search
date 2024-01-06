from src import helpers


def widget(word):
    definitions = helpers.makeJSONRequest(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if type(definitions) is not list:
        return {
            "type": "dictionary",
            "content": False
        }
    definitions = definitions[0]

    return {
        "type": "dictionary",
        "content": definitions
    }
