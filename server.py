from flask import Flask
from src import helpers

app = Flask(__name__, static_folder="static", static_url_path="")
app.jinja_env.filters['highlight_query_words'] = helpers.highlight_query_words
app.jinja_env.globals.update(int=int)
