from src.widgets import (
    dictionary,
)


def _check_dictionary(links):
    allowed_urls = (
        'merriam-webster.com/dictionary/',
        'https://www.dictionary.com/browse/',
        'https://www.collinsdictionary.com/us/dictionary/english/'
    )
    # Loops over all the links to check if any of them start with
    # any of the `allowed_urls`
    for link in links:
        if "#:~:" in link:
            link = link.split("#:~:")[0]
        if link.startswith(allowed_urls):
            # Returns the last part of the URL, which is the word to be defined.
            if link[-1] == "/":
                link = link[:-1]
            return link.split("/")[-1]
    return ""


def check_for_widgets(query, links, soup):
    """
    Checks if there's anything to indicate that a widget should be shown.

    Args:
        query: For checking if the query contains a string that might indicate
               need for a widget. E.g. 'Weather in X' should show a widget for the weather.

        links: looking over links to see if there's any sites that would suggest
                 need for a widget. E.g. If a result has 'dictionary.com' in the URL,
                 the user's probably looking for the definition of a word.

        soup: Checking for the existence of an element. E.g. if the element for news
              results is present, there should be a widget for news.
    """
    define = _check_dictionary(links)
    if define != "":
        return dictionary.widget(define)

    # Return false if all other check fail.
    return False
