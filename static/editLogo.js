let logo = document.querySelector(".search-container h1");
let localLogoName = localStorage.getItem("logo_name");
let topLogo = document.querySelector("#prev-next-form h1 a")

if (localLogoName !== null && topLogo !== null) {
  topLogo.innerText = localLogoName;
}

if (logo != null) {
  if (localLogoName !== null)
    logo.innerText = localLogoName;

  logo.contentEditable = true;
  logo.spellcheck = false;
  logo.addEventListener("input", () => {
    localStorage.setItem("logo_name", logo.innerText.replace("\n", ""));
  });
}
