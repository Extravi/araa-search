from flask import render_template, request
import requests
import json
from server import app


@app.route("/switch_instance")
def switch_instance_page():
    instances = json.loads(requests.get(
        "https://raw.githubusercontent.com/amogusussy/tailsx/switch-instances/instances.json"
    ))

    q = request.args.get("q")
    t = request.args.get("t")
    p = request.args.get("p")

    return render_template("switch_instances.html", 
                           instances=instances, q=q, t=t, p=p
                           )
