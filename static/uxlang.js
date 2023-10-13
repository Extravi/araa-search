/**
 * @source: ./uxlang.js
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

function mapToValidLanguage(userLanguage) {
    const languageMappings = {
        "en": "english",
        "da": "danish",
        "nl": "dutch",
        "fr": "french",
        "fr-CA": "french_canadian",
        "de": "german",
        "el": "greek",
        "it": "italian",
        "ja": "japanese",
        "ko": "korean",
        "zh": "mandarin_chinese",
        "no": "norwegian",
        "pl": "polish",
        "pt": "portuguese",
        "ru": "russian",
        "es": "spanish",
        "sv": "swedish",
        "tr": "turkish",
        "uk": "ukrainian"
    };

    const browserLanguage = userLanguage.split("-")[0];
    return languageMappings[browserLanguage] || "english";
}

function setLanguageCookie() {
    const userLanguage = navigator.language.toLowerCase();
    const mappedLanguage = mapToValidLanguage(userLanguage);
    setCookie("ux_lang", mappedLanguage);
    window.location.reload();
}

if (!document.cookie.includes("ux_lang")) {
    setLanguageCookie();
}
