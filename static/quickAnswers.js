function getAnswers(query) {
  return fetch(`/answers?q=${encodeURIComponent(query)}`)
    .then(response => {
      return response.json();
    })
    .catch(error => {
      console.error(error);
      throw error;
    });
}

function applyAnswers() {
  let params = new URLSearchParams(window.location.search);
  let query = params.get("q");

  getAnswers(query)
    .then(data => {
      addToPage(data);
    })
    .catch(error => {
      console.error(error);
      return
    });
}

function getElemByReference(ref) {
  let results = [];
  let selectResults = document.querySelectorAll(".block")
  for (let i = 0; i < selectResults.length; i++) {
    elem = selectResults[i];
    if (elem.attributes['data-ref'].nodeValue.includes(String(ref))) {
      results.push(elem);
    }
  }
  return results;
}

function addToPage(data) {
  if (data['status'] == 'failed') {
    return;
  }
  let result = data['results'][0]

  let answerBox = document.createElement('div');
  answerBox.className = "answer-box";

  let answerText = document.createElement("div");
  answerText.innerHTML = result.text;
  answerText.className = "answer-text";

  let references = document.createElement("div");
  references.className = "references";
  for (let i = 0; i < result['references'].length; i++) {
    ref = result['references'][i]
    let reference = document.createElement("a");
    reference.innerText = String(i) + " - " + ref['name'];
    reference['href'] = ref['url'];
    reference.classList = "reference";
    reference.classList.add("ref-" + i);
    reference.refID = i;
    reference.addEventListener('mouseenter', () => {
      results = getElemByReference(i);
      for (let i = 0; i < results.length; i++) {
        results[i].style.background = '#404042';
      }
    })
    reference.addEventListener('mouseleave', (e) => {
      results = getElemByReference(i);
      for (let i = 0; i < results.length; i++) {
        results[i].style.background = '';
      }
    })
    references.append(reference)
  }

  answerStrings = answerText.querySelectorAll(".block");
  for (let i = 0; i < answerStrings.length; i++) {
    let elem = answerStrings[i];
    let refs = elem.attributes['data-ref'].nodeValue.split("-");
    elem.addEventListener("mouseenter", () => {
      for (const j of refs) {
        document.querySelector(".ref-" + j).style.background = '#404042'
      }
    })
    elem.addEventListener("mouseleave", () => {
      for (const j of refs) {
        document.querySelector(".ref-" + j).style.background = ''
      }
    })
  }

  answerBox.prepend(answerText);
  answerBox.append(references);

  document.querySelector(".fetched").after(answerBox);

  document.querySelector(".snip").style.marginTop = "-270px"
}

applyAnswers();
