const searchInput = document.getElementById('search-input');
const searchWrapper = document.querySelectorAll('.wrapper, .wrapper-results')[0];
const resultsWrapper = document.querySelector('.autocomplete');

async function getSuggestions(query) {
  try {
    const response = await fetch(`/suggestions?q=${query}`);
    const data = await response.json();
    return data[1]; // Return only the array of suggestion strings
  } catch (error) {
    console.error(error);
  }
}

let currentIndex = -1; // Keep track of the currently selected suggestion
let userUpdate = false; // Flag to track if the value of the search input was updated by the user

searchInput.addEventListener('input', () => {
  userUpdate = true; // Set the flag to true when the value of the search input is updated by the user
});

searchInput.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
    event.preventDefault(); // Prevent the cursor from moving in the search input

    // Find the currently selected suggestion element
    const selectedSuggestion = resultsWrapper.querySelector('.selected');
    if (selectedSuggestion) {
      selectedSuggestion.classList.remove('selected'); // Deselect the currently selected suggestion
    }

    // Increment or decrement the current index based on the arrow key pressed
    if (event.key === 'ArrowUp') {
      currentIndex--;
    } else {
      currentIndex++;
    }

    // Wrap around the index if it goes out of bounds
    if (currentIndex < 0) {
      currentIndex = resultsWrapper.querySelectorAll('li').length - 1;
    } else if (currentIndex >= resultsWrapper.querySelectorAll('li').length) {
      currentIndex = 0;
    }

    // Select the new suggestion
    resultsWrapper.querySelectorAll('li')[currentIndex].classList.add('selected');
    // Update the value of the search input
    searchInput.value = resultsWrapper.querySelectorAll('li')[currentIndex].textContent;
  }
});

searchInput.addEventListener('keyup', async (event) => {
  if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') {
    let results = [];
    let input = searchInput.value;
    if (input.length && userUpdate) {
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

  // Only show the autocomplete suggestions if the search input has a non-empty value
  if (searchInput.value) {
    searchWrapper.classList.add('show');
  }
  resultsWrapper.innerHTML = `<ul>${content}</ul>`;
}

resultsWrapper.addEventListener('click', (event) => {
  if (event.target.tagName === 'LI') {
    // Set the value of the search input to the clicked suggestion
    searchInput.value = event.target.textContent;
    // Reset the current index
    currentIndex = -1;
    // Submit the form
    searchWrapper.querySelector('input[type="submit"]').click();
    // Remove the show class from the search wrapper
    searchWrapper.classList.remove('show');
  }
});

// Add event listener to hide autocomplete suggestions when clicking outside of search-input or wrapper
document.addEventListener('click', (event) => {
  // Check if the target of the event is the search-input or any of its ancestors
  if (!searchInput.contains(event.target) && !searchWrapper.contains(event.target)) {
    // Hide the autocomplete suggestions
    searchWrapper.classList.remove('show');
  }
});

// Add event listener to show autocomplete suggestions when clicking on search-input with non-empty value
searchInput.addEventListener('click', () => {
  if (searchInput.value) {
    searchWrapper.classList.add('show');
  }
});
