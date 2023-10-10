/**
 * @source: ./cookies-settings-version.js
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

document.addEventListener("DOMContentLoaded", function () {
    const saveButton = document.querySelector(".save-settings-page");

    if (saveButton) {
        saveButton.addEventListener("click", function () {
            const langSelect = document.querySelector("#lang");
            const domainSelect = document.querySelector("#domain");
            const themeSelect = document.querySelector("#theme");
            const safeSelect = document.querySelector("#safe");
            const newTabSelect = document.querySelector("#open-new-tab");

            if (langSelect) {
                const selectedOption = langSelect.options[langSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie("lang", selectedValue);
            }

            if (domainSelect) {
                const selectedOption = domainSelect.options[domainSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie("domain", selectedValue);
            }

            if (themeSelect) {
                const selectedOption = themeSelect.options[themeSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie("theme", selectedValue);
            }

            if (safeSelect) {
                const selectedOption = safeSelect.options[safeSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie("safe", selectedValue);
            }

            if (newTabSelect) {
                const selectedOption = newTabSelect.options[newTabSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie("new_tab", selectedValue);
            }
        });
    }
});

document.getElementById("discoverButton").addEventListener("click", function (event) {
    event.preventDefault();
    window.location.href = "/discover";
});