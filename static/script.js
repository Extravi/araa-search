/**
 * @source: ./script.js
 * 
 * @licstart  The following is the entire license notice for the
 *  JavaScript code in this page.
 * 
 * Copyright (C) 2023  Extravi
 * 
 * The JavaScript code in this page is free software: you can
 * redistribute it and/or modify it under the terms of the GNU Affero
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * 
 * The code is distributed WITHOUT ANY WARRANTY; without even the
 * implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Affero General Public License for more details.
 * 
 * As additional permission under GNU Affero General Public License
 * section 7, you may distribute non-source (e.g., minimized or compacted)
 * forms of that code without the copy of the GNU Affero General Public
 * License normally required by section 4, provided you include this
 * license notice and a URL through which recipients can access the
 * Corresponding Source.
 * 
 * @licend  The above is the entire license notice
 *  for the JavaScript code in this page.
 */

// Removes the 'Apply Settings' button for Javascript users, 
// since changing any of the elements causes the settings to apply
// automatically.
let resultsSave = document.querySelector(".results-save");
if (resultsSave != null) {
  resultsSave.style.display = "none";
}

const searchInput = document.getElementById('search-input');
const searchWrapper = document.querySelectorAll('.wrapper, .wrapper-results')[0];
const resultsWrapper = document.querySelector('.autocomplete');

async function getSuggestions(query) {
  try {
    params = new URLSearchParams({"q": query}).toString();
    const response = await fetch(`/suggestions?${params}`);
    const data = await response.json();
    return data[1]; // Return only the array of suggestion strings
  } catch (error) {
    console.error(error);
  }
}

let currentIndex = -1; // Keep track of the currently selected suggestion

searchInput.addEventListener('input', async () => {
  let results = [];
  let input = searchInput.value;
  if (input.length) {
    results = await getSuggestions(input);
  }
  renderResults(results);
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
    // Remove the show class from the search wrapper
    searchWrapper.classList.remove('show');
  }
});

// Load material icons. If the file cannot be loaded,
// skip them and put a warning in the console.
const font = new FontFace('Material Icons Round', 'url("/fonts/material-icons-round-v108-latin-regular.woff2") format("woff2")');
font.load().then(() => {
  const icons = document.getElementsByClassName('material-icons-round');

  // Display all icons.
  for (let icon of icons) {
    icon.style.visibility = 'visible';
  }

  // Ensure icons for the different types of searches are sized correctly.
  document.querySelectorAll('#sub-search-wrapper-ico').forEach((el) => {
    el.style.fontSize = '17px';
  });
}).catch(() => {
  console.warn('Failed to load Material Icons Round. Hiding any icons using said pack.');
});

// load image after server side processing
window.addEventListener('DOMContentLoaded', function() {
  var knoTitleElement = document.getElementById('kno_title');
  var kno_title = knoTitleElement.dataset.knoTitle;
  fetch(kno_title)
  .then(response => response.json())
  .then(data => {
    const pageId = Object.keys(data.query.pages)[0];
    const thumbnailSource = data.query.pages[pageId].thumbnail.source;
    const url = "/img_proxy?url=" + thumbnailSource;

    // update the img tag with url and add kno_wiki_show
    var imgElement = document.querySelector('.kno_wiki');
    imgElement.src = url;
    imgElement.classList.add('kno_wiki_show');

    console.log(url);
  })
  .catch(error => {
    console.log('Error fetching data:', error);
  });
});

const urlParams = new URLSearchParams(window.location.search);

if (urlParams.get("t") === "image") {

  // image viewer for image search
  const closeButton = document.querySelector('.image-close');
  const imageView = document.querySelector('.image_view');
  const images = document.querySelector('.images');
  const viewImageImg = document.querySelector('.view-image-img');
  const proxyLinkUwu = document.querySelector('.proxy-link-uwu');
  const imageSource = document.querySelector('.image-source');
  const imageViewerLink = document.querySelector('.image-viewer-link');
  const imageSize = document.querySelector('.image-size');
  const imageAlt = document.querySelector('.image-alt');
  const openImageViewer = document.querySelectorAll('.open-image-viewer');
  const imageBefore = document.querySelector('.image-before');
  const imageNext = document.querySelector('.image-next');
  let currentImageIndex = 0;

  closeButton.addEventListener('click', function() {
    imageView.classList.remove('image_show');
    imageView.classList.add('image_hide');
    images.classList.add('images_viewer_hidden');
  });

  openImageViewer.forEach((image, index) => {
    image.addEventListener('click', function(event) {
      event.preventDefault();
      currentImageIndex = index;
      showImage();
    });
  });

  imageBefore.addEventListener('click', function() {
    currentImageIndex = (currentImageIndex - 1 + openImageViewer.length) % openImageViewer.length;
    showImage();
  });

  document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
      currentImageIndex = (currentImageIndex - 1 + openImageViewer.length) % openImageViewer.length;
      showImage();
    }
  });

  imageNext.addEventListener('click', function() {
    currentImageIndex = (currentImageIndex + 1) % openImageViewer.length;
    showImage();
  });

  document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowRight') {
      currentImageIndex = (currentImageIndex + 1) % openImageViewer.length;
      showImage();
    }
  });

  function showImage() {
    const src = openImageViewer[currentImageIndex].getAttribute('src');
    const alt = openImageViewer[currentImageIndex].getAttribute('alt');
    const clickableLink = openImageViewer[currentImageIndex].closest('.clickable');
    const href = clickableLink.getAttribute('href');
    viewImageImg.src = src;
    proxyLinkUwu.href = src;
    imageSource.href = href;
    imageViewerLink.href = href;
    imageSource.textContent = href;
    images.classList.remove('images_viewer_hidden');
    imageView.classList.remove('image_hide');
    imageView.classList.add('image_show');
    imageAlt.textContent = alt;

    getImageSize(src).then(size => {
      imageSize.textContent = size;
    });
  }

  function getImageSize(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = function() {
        const size = `${this.width} x ${this.height}`;
        resolve(size);
      };
      img.onerror = function() {
        reject('Error loading image');
      };
      img.src = url;
    });
  }
}
