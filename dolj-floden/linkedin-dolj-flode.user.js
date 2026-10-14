// ==UserScript==
// @name         LinkedIn – dölj flödet
// @description  Döljer inläggsflödet på LinkedIns startsida. Rutan för att skriva inlägg, menyn och allt utanför startsidan lämnas orört.
// @version      1.0
// @match        *://*.linkedin.com/*
// @run-at       document-start
// @inject-into  content
// ==/UserScript==

(function () {
  "use strict";

  const ON = "tidskoll-flode-dolt";

  // Bara startsidan. Enskilda inlägg (/feed/update/...) ska gå att öppna som vanligt.
  const isHome = () => /^\/(feed\/?)?$/.test(location.pathname);

  // Datorn: LinkedIn slumpar sina klassnamn, men flödeslistan bär data-testid="mainFeed".
  // Första barnet är rutan för att skriva inlägg; allt efter det är flödet,
  // sorteringsvalet, "Nya inlägg" och "Ladda mer".
  // Mobilen (Safari på iPhone) får en annan sida där flödet är ol.feed-container.
  const css = `
    html.${ON} [data-testid="mainFeed"] > :not(:first-child),
    html.${ON} section.feeds .feed-container,
    html.${ON} #new-content-pill {
      display: none !important;
    }
    #tidskoll-flode-notis { display: none; }
    html.${ON} #tidskoll-flode-notis {
      display: block;
      padding: 32px 16px;
      text-align: center;
      font-size: 14px;
      color: inherit;
      opacity: 0.6;
    }
  `;

  function addStyle() {
    if (document.getElementById("tidskoll-flode-stil")) return;
    const style = document.createElement("style");
    style.id = "tidskoll-flode-stil";
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }

  function addNote() {
    const feed = document.querySelector('[data-testid="mainFeed"], section.feeds .feed-container');
    if (!feed || document.getElementById("tidskoll-flode-notis")) return;
    const note = document.createElement("div");
    note.id = "tidskoll-flode-notis";
    note.textContent = "Flödet är dolt.";
    feed.after(note);
  }

  function update() {
    addStyle();
    document.documentElement.classList.toggle(ON, isHome());
    if (isHome()) addNote();
  }

  update();

  // LinkedIn byter sida utan omladdning, så läget kontrolleras löpande.
  setInterval(update, 500);
})();
