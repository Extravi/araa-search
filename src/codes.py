from src.helpers import makeJSONRequest, latest_commit
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json

def codeResults(query) -> Response:
    start_time = time.time()
    api = request.args.get("api", "false")
    data = makeJSONRequest(f"https://api.stackexchange.com/2.3/search?order=desc&sort=activity&intitle={query}&site=stackoverflow&filter=!*MQI_nAyQ(DMBtaFC*6Ry5W_Dfka&pagesize=20")


    items = data["items"]

    questionsTitles = []
    hrefs = []
    acceptedAnswersBodies = []

    results = []
    for item in items:
        if("accepted_answer_id" in item):
            questionsTitles.append(item["title"])
            hrefs.append(item["link"])
            acceptedAnswerId = item["accepted_answer_id"]
            answerData = makeJSONRequest(f"https://api.stackexchange.com/2.3/answers/{acceptedAnswerId}?order=desc&sort=activity&site=stackoverflow&filter=!-)ZoK(1l90pT")
            acceptedAnswersBodies.append(answerData["items"][0]["body"])
                

    for questionTitle, href, acceptedAnswerBody in zip(questionsTitles, hrefs,  acceptedAnswersBodies):
        results.append([questionTitle, href, acceptedAnswerBody])


    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true":
        return jsonify(results)
    else:
        return render_template("code.html", results=results, title=f"{query} - TailsX",
            q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
            theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
            javascript=request.cookies.get('javascript', 'enabled'), type="code",
            new_tab=request.cookies.get("new_tab"), repo_url=REPO, commit=latest_commit())
