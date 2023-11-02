/**
 * @source: ./menu.js
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

const menuVisible = document.querySelector('.search-menu');
const menuDiv = document.querySelector('.settings-search-div-search');

function getCookie(name) {
    const cookies = document.cookie.split("; ");
    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.split("=");
        if (cookieName === name) {
            return cookieValue;
        }
    }
    return null;
}

function setThemeBasedOnCookie() {
    const themeCookie = getCookie("theme");
    const themeNameSpan = document.getElementById("theme_name");
    const themes = {
        "dark_blur": "Dark (Default)",
        "dark_default": "Dark (no background)",
        "light": "Light",
    };

    if (themes.hasOwnProperty(themeCookie)) {
        themeNameSpan.textContent = themes[themeCookie];
    }
}

setThemeBasedOnCookie();

document.getElementById("settingsButton").addEventListener("click", function () {
    window.location.href = "/settings";
});

menuDiv.addEventListener('click', function (event) {
    event.stopPropagation();

    if (menuVisible.classList.contains('settings-menu-visible')) {
        menuVisible.classList.remove('settings-menu-visible');
        menuVisible.classList.add('settings-menu-hidden');
    } else {
        menuVisible.classList.remove('settings-menu-hidden');
        menuVisible.classList.add('settings-menu-visible');
    }
});

document.addEventListener('click', function (event) {
    if (!menuDiv.contains(event.target) && !menuVisible.contains(event.target)) {
        menuVisible.classList.remove('settings-menu-visible');
        menuVisible.classList.add('settings-menu-hidden');
    }
});
