const searchInput = document.getElementById('search-input');
const searchWrapper = document.querySelectorAll('.wrapper, .wrapper-results')[0];
const resultsWrapper = document.querySelector('.autocomplete');

async function getSuggestions(query) {
  try {
    const response = await fetch(`http://127.0.0.1:8000/suggestions?q=${query}`);
    const data = await response.json();
    return data[1]; // Return only the array of suggestion strings
  } catch (error) {
    console.error(error);
  }
}

searchInput.addEventListener('keyup', async () => {
  let results = [];
  let input = searchInput.value;
  if (input.length) {
    results = await getSuggestions(input);
  }
  renderResults(results);
});

searchWrapper.addEventListener('click', async (event) => {
  // Only show the suggestions if the search input was clicked, not the wrapper itself
  if (event.target === searchInput) {
    let results = [];
    let input = searchInput.value;
    if (input.length) {
      results = await getSuggestions(input);
    }
    renderResults(results);
  }
});

function renderResults(results) {
  if (!results || !results.length || !searchInput.value) {
    return searchWrapper.classList.remove('show');
  }

  let content = '';
  results.forEach((item) => {
    content += `<li>${item}</li>`;
  });

  searchWrapper.classList.add('show');
  resultsWrapper.innerHTML = `<ul>${content}</ul>`;
}

resultsWrapper.addEventListener('click', (event) => {
  if (event.target.tagName === 'LI') {
    // Set the value of the search input to the clicked suggestion
    searchInput.value = event.target.textContent;
    // Submit the form
    searchWrapper.querySelector('input[type="submit"]').click();
  }
});

document.addEventListener('click', (event) => {
  if (!searchWrapper.contains(event.target)) {
    searchWrapper.classList.remove('show');
  }
});
