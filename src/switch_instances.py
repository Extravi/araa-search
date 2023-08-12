from flask import render_template, request
import requests
import json


@app.route("/switch_instance")
def switch_instance_page():
    instances = json.loads(requests.get(
        ""
    ))
