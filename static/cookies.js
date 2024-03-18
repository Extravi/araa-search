/**
 * @source: ./cookies.js
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

function setCookie(name, value) {
    document.cookie = `${name}=${value}; HostOnly=true; SameSite=None; Secure; Max-Age=2147483647`;
}

function reloadPageForTheme() {
    const themeCookie = document.cookie.split(";").find((cookie) => cookie.trim().startsWith("theme="));

    if (themeCookie) {
        window.location.reload();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const langSelect = document.querySelector(".lang");

    if (langSelect) {
        langSelect.addEventListener("change", function () {
            const selectedOption = langSelect.options[langSelect.selectedIndex];
            const selectedValue = selectedOption.value;
            setCookie("lang", selectedValue);
            window.location.reload();
        });
    }

    const domainSelect = document.querySelector(".domain");

    if (domainSelect) {
        domainSelect.addEventListener("change", function () {
            const selectedOption = domainSelect.options[domainSelect.selectedIndex];
            const selectedValue = selectedOption.value;
            setCookie("domain", selectedValue);
            window.location.reload();
        });
    }

    const themeDivs = document.querySelectorAll(".themes-settings-menu div");

    themeDivs.forEach(function (div) {
        div.addEventListener("click", function () {
            const clickedDivId = div.firstElementChild.id;
            setCookie("theme", clickedDivId);
            reloadPageForTheme();
        });
    });

    const safeSearchSelect = document.getElementById("safeSearchSelect");

    if (safeSearchSelect) {
        safeSearchSelect.addEventListener("change", function () {
            const selectedValue = safeSearchSelect.value;
            setCookie("safe", selectedValue);
            window.location.reload();
        });
    }

    const languageSelect = document.getElementById("languageSelect");

    if (languageSelect) {
        languageSelect.addEventListener("change", function () {
            const selectedValue = languageSelect.value;
            setCookie("lang", selectedValue);
            window.location.reload();
        });
    }
});
