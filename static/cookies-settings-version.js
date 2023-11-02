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

    if (saveButton != null) {
        saveButton.addEventListener("click", function () {
            let setting_list = ["lang", "domain", "theme", "safe", "open-new-tab", "ux_lang"];
            for (let i = 0; i < setting_list.length; i++) {
              setting = setting_list[i];
              settingSelect = document.getElementById(setting);
              if (settingSelect) {
                const selectedOption = settingSelect.options[settingSelect.selectedIndex];
                const selectedValue = selectedOption.value;
                setCookie(setting, selectedValue);
              }
            }
        });
    }
});

document.getElementById("discoverButton").addEventListener("click", function (event) {
    event.preventDefault();
    window.location.href = "/discover";
});
