// Scripts for the website. Jupyter Book adds each JS file in _static/ to every page of the book, also to pages
// that are added later. Four parts: hidden parts of the book (below), collapsible sections, the buttons of the
// dropdowns of the course's pages, and the update check (at the end).
//
// Hidden parts of the book (yr/README.md, "A hidden part of the book"). A part whose name is in YR_HIDDEN_PARTS
// is in the book, but a reader does not see it: the menu, the "next" and "previous" links and every other link
// do not show its pages, and a page of the part shows "This page is not available." The pages of the part NAME
// are yr/NAME_*.md. The part shows when the address of any page of the book ends with ?show=NAME (several
// names: ?show=NAME1,NAME2). The browser tab then keeps showing it, and the links of the book carry ?show=NAME
// to the next page. ?show=none hides the part again. This hides the part from a reader of the website. It does
// not protect it: the text is in the HTML of the pages and in the repository.
// To make a part visible to everyone: yr/README.md, "A hidden part of the book".
// No part is hidden now. Do not add a name here before you read yr/README.md, "A hidden part of the book".
const YR_HIDDEN_PARTS = [];
(() => {
  const KEY = 'yr-show';
  let shown = [];
  try { shown = (sessionStorage.getItem(KEY) || '').split(',').filter(Boolean); } catch (e) { /* no storage */ }
  const param = new URLSearchParams(location.search).get('show');
  if (param !== null) {  // the address decides: ?show=NAME shows, ?show=none (or any other value) hides
    shown = param.split(',').map((name) => name.trim()).filter((name) => YR_HIDDEN_PARTS.includes(name));
    try { sessionStorage.setItem(KEY, shown.join(',')); } catch (e) { /* no storage: this page only */ }
  }
  shown = shown.filter((name) => YR_HIDDEN_PARTS.includes(name));
  const hidden = YR_HIDDEN_PARTS.filter((name) => !shown.includes(name));
  const partOfPage = YR_HIDDEN_PARTS.find((name) => new RegExp('/' + name + '_[^/]*$').test(location.pathname));
  const blocked = partOfPage !== undefined && hidden.includes(partOfPage);
  const linkTo = (name) => 'a[href*="' + name + '_"]';

  // This script runs in <head>, before the page is drawn: a style hides the part at once, without a flash.
  const rules = hidden.map((name) =>
    'nav li:has(> ' + linkTo(name) + '), nav p.caption:has(+ ul > li > ' + linkTo(name) + '), ' + linkTo(name) +
    ' { display: none !important; }');
  if (blocked) {
    document.documentElement.classList.add('yr-hidden-page');  // yr.css hides the content of the page
    document.title = 'Think Python';
  }
  if (rules.length) {
    const style = document.createElement('style');
    style.textContent = rules.join('\n');
    document.head.append(style);
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Take the hidden parts out of the page (also for a browser without :has() in CSS).
    hidden.forEach((name) => {
      document.querySelectorAll(linkTo(name)).forEach((link) => {
        const item = link.closest('nav li.toctree-l1, nav li.toctree-l2, nav li.toctree-l3');
        const list = item && item.closest('ul.bd-sidenav');
        (item || link).remove();
        if (list && !list.querySelector('li')) {  // the part is empty now: remove its caption too
          const caption = list.previousElementSibling;
          if (caption && caption.matches('p.caption')) caption.remove();
          list.remove();
        }
      });
    });
    if (blocked) {
      // The menu marks the page that is open with href="#": remove the part that holds it, and say that the
      // page is not available.
      const list = document.querySelector('nav.bd-links ul.current.bd-sidenav');
      if (list) {
        const caption = list.previousElementSibling;
        if (caption && caption.matches('p.caption')) caption.remove();
        list.remove();
      }
      const main = document.getElementById('main-content');
      if (main) {
        const note = document.createElement('div');
        note.className = 'yr-not-available';
        const text = document.createElement('p');
        text.textContent = 'This page is not available.';
        const home = document.createElement('a');
        home.href = document.querySelector('a.navbar-brand')?.href || '../index.html';
        home.textContent = 'Go to the first page of the book';
        note.append(text, home);
        main.prepend(note);
      }
      return;
    }
    if (!shown.length) return;
    // The part shows. Its pages say so at the top, and the links of the book keep ?show=NAME.
    if (partOfPage !== undefined) {
      const title = document.querySelector('article.bd-article h1');
      if (title) {
        const note = document.createElement('p');
        note.className = 'yr-hidden-note';
        note.textContent = 'A hidden page: readers of the website do not see it. It shows because the address ' +
          'had ?show=' + partOfPage + '. To hide it again in this tab, add ?show=none to the address.';
        title.before(note);
      }
    }
    document.querySelectorAll('a[href]').forEach((link) => {
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || /^(mailto|javascript):/.test(href)) return;
      let url;
      try { url = new URL(link.href); } catch (e) { return; }
      if (url.origin !== location.origin || !/(\.html|\/)$/.test(url.pathname)) return;  // pages of this book only
      url.searchParams.set('show', shown.join(','));
      link.href = url.href;
    });
  });
})();

// Collapsible sections. In Colab, the reader can collapse any heading. On the website, this script puts a
// heading and the rest of its section in a <details> block, open at the start: a click on the heading hides or
// shows the section.
// - A page with <div class="yr-collapse-all"></div> (in any markdown cell): every section with a ##, ### or
//   #### heading is collapsible, and each of these headings has the buttons "Focus here", "Collapse all" and
//   "Expand all". "Focus here" shows only this section (open, with the sections in it). All the other sections
//   are closed. The sections that contain it stay open, but they show only their headings and the path to
//   this section (class yr-focus-path); a click on one of these headings shows the rest of it. The buttons
//   change only these sections, not the Answer and "Diving deeper" boxes.
// - On other pages, only a section whose heading cell has <div class="yr-collapse"> is collapsible.
document.addEventListener('DOMContentLoaded', () => {
  const HEADINGS = ':scope > h2, :scope > h3, :scope > h4';
  const all = document.querySelector('div.yr-collapse-all') !== null;
  const sections = all
    ? [...document.querySelectorAll('section')].filter((s) => s.querySelector(HEADINGS))
    : [...document.querySelectorAll('section > div.yr-collapse')].map((marker) => marker.parentElement);

  const PATH_TIP = 'Click to show all of this section';
  const clearFocus = () => {
    document.querySelectorAll('details.yr-focus-path').forEach((box) => {
      box.classList.remove('yr-focus-path');
      box.querySelector(':scope > summary').removeAttribute('title');
    });
  };
  const setAll = (open) => {
    clearFocus();
    document.querySelectorAll('details.yr-collapse').forEach((box) => { box.open = open; });
  };
  const focus = (box) => {
    setAll(false);
    box.open = true;
    box.querySelectorAll('details.yr-collapse').forEach((inner) => { inner.open = true; });
    // The outer sections stay open, but show only their headings and the path to this section (yr.css).
    for (let b = box.parentElement.closest('details.yr-collapse'); b; b = b.parentElement.closest('details.yr-collapse')) {
      b.open = true;
      b.classList.add('yr-focus-path');
      b.querySelector(':scope > summary').title = PATH_TIP;
    }
  };
  const button = (text, className, action, summary) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = className;
    b.textContent = text;
    b.addEventListener('click', (event) => {
      event.preventDefault();  // a click in a <summary> also opens or closes its <details>: stop that
      event.stopPropagation();
      action();
      summary.scrollIntoView({ block: 'start' });  // keep the heading that was clicked in view
    });
    return b;
  };

  sections.forEach((section) => {
    const heading = section.querySelector(HEADINGS);
    if (!heading) return;
    const box = document.createElement('details');
    box.className = 'yr-collapse';
    box.open = true;
    const summary = document.createElement('summary');
    heading.before(box);
    summary.append(heading);
    if (all) {
      const group = document.createElement('span');  // the two buttons stay together, also when the line wraps
      group.className = 'yr-toggle-group';
      group.append(
        button('Focus here', 'yr-toggle-all yr-focus', () => focus(box), summary),
        button('Collapse all', 'yr-toggle-all', () => setAll(false), summary),
        button('Expand all', 'yr-toggle-all', () => setAll(true), summary),
      );
      summary.append(group);
    }
    box.append(summary);
    while (box.nextSibling) box.append(box.nextSibling);
    // After "Focus here", a click on the heading of an outer section shows all of it (and does not close it).
    summary.addEventListener('click', (event) => {
      if (!box.classList.contains('yr-focus-path')) return;
      event.preventDefault();
      clearFocus();
    });
  });

  // A link to a part of a closed section (for example, from the Contents list) opens the section.
  const openTarget = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = id && document.getElementById(id);
    if (!target) return;
    clearFocus();
    for (let box = target.closest('details.yr-collapse'); box; box = box.parentElement.closest('details.yr-collapse')) {
      box.open = true;
    }
    target.scrollIntoView();
  };
  window.addEventListener('hashchange', openTarget);
  openTarget();
});

// The buttons of the dropdowns of the course's pages (pages in yr/). The build makes each Answer, each concept
// list ("Python Syntax and Semantics", "Definitions, etc.") and each "Diving deeper" box a dropdown: an
// admonition with the class "dropdown" (jb/prep_notebooks.py). sphinx-togglebutton adds a click handler to its
// title, and a hint "Click to show" (yr.css hides this hint on these pages). This script adds to the title:
// - of every dropdown: the button "Expand/Collapse", which opens or closes this dropdown;
// - of each Answer: also "Expand all" and "Collapse all", which open or close all the Answers of the page.
document.addEventListener('DOMContentLoaded', () => {
  if (!location.pathname.includes('/yr/') || typeof toggleHidden !== 'function') return;
  const answers = [];
  const isOpen = (box) => !box.classList.contains('toggle-hidden');
  const setOpen = (box, open) => {
    const toggle = box.querySelector(':scope > .admonition-title > button.toggle-button');
    if (toggle && isOpen(box) !== open) toggleHidden(toggle);  // sphinx-togglebutton's function
  };
  const button = (text, className, action) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'yr-dd-button ' + className;
    b.textContent = text;
    b.addEventListener('click', (event) => {
      event.stopPropagation();  // the click handler of the title would also open or close the dropdown
      action();
    });
    return b;
  };

  document.querySelectorAll('.admonition.dropdown').forEach((box) => {
    const title = box.querySelector(':scope > .admonition-title');
    if (!title || !title.querySelector('button.toggle-button')) return;
    box.classList.add('yr-dd');
    const group = document.createElement('span');
    group.className = 'yr-dd-group';
    group.append(button('Expand/Collapse', 'yr-dd-main', () => setOpen(box, !isOpen(box))));
    if (title.textContent.trim() === 'Answer') {
      answers.push(box);
      group.append(
        button('Expand all', 'yr-dd-all', () => answers.forEach((a) => setOpen(a, true))),
        button('Collapse all', 'yr-dd-all', () => answers.forEach((a) => setOpen(a, false))),
      );
    }
    title.querySelector('button.toggle-button').before(group);
  });
});

// Update check (every page). A browser can show a copy of a page that it saved before (GitHub Pages lets it keep a
// copy for 10 minutes), and a tab that stays open keeps the old version. So the page asks the server, without
// any saved copy, for the date when the page was published (the Last-Modified header), and compares it with the
// date of the copy on the screen (document.lastModified). A newer date means that a new version was published:
// - when the reader comes back to the tab (from another tab or window), the page reloads at once: the reader
//   was away, so a reload does not interrupt the reading;
// - while the reader looks at the page, a bar at the top offers "Reload".
// After a reload, the page goes back to the same place. The check runs 3 seconds after the page loads, every
// 5 minutes while the page is on the screen, and each time that the reader comes back to the tab.
(() => {
  if (!/^https?:$/.test(location.protocol)) return;  // not for a page opened from a file
  const SCROLL_KEY = 'yr-scroll:' + location.pathname;
  const shown = new Date(document.lastModified).getTime();
  let newer = false;

  const reload = () => {
    try { sessionStorage.setItem(SCROLL_KEY, String(window.scrollY)); } catch (e) { /* no storage: reload anyway */ }
    location.reload();
  };

  const showBar = () => {
    if (document.getElementById('yr-update-bar')) return;
    const bar = document.createElement('div');
    bar.id = 'yr-update-bar';
    bar.setAttribute('role', 'status');
    const text = document.createElement('span');
    text.textContent = 'A new version of this website was published.';
    const now = document.createElement('button');
    now.type = 'button';
    now.textContent = 'Reload';
    now.addEventListener('click', reload);
    const later = document.createElement('button');
    later.type = 'button';
    later.className = 'yr-update-later';
    later.textContent = 'Later';
    later.addEventListener('click', () => bar.remove());
    bar.append(text, now, later);
    document.body.prepend(bar);
  };

  const check = async (comingBack) => {
    if (newer) {
      if (comingBack) reload();
      return;
    }
    try {
      const url = location.pathname + '?yr-update-check=' + Date.now();  // a new URL: no saved copy can answer
      const response = await fetch(url, { method: 'HEAD', cache: 'no-store' });
      const published = new Date(response.headers.get('Last-Modified')).getTime();
      if (!(published > shown + 1000)) return;  // the same version (or no date)
      newer = true;
      if (comingBack) reload();
      else if (!document.hidden) showBar();  // a hidden tab reloads when the reader comes back to it
    } catch (e) {
      // no network: try again at the next check
    }
  };

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) check(true);
  });
  setTimeout(() => check(false), 3000);
  setInterval(() => { if (!document.hidden) check(false); }, 5 * 60 * 1000);

  // After a reload by the update check: go back to the same place on the page.
  window.addEventListener('load', () => {
    let y = null;
    try { y = sessionStorage.getItem(SCROLL_KEY); sessionStorage.removeItem(SCROLL_KEY); } catch (e) { /* none */ }
    if (y !== null) window.scrollTo(0, Number(y));
  });
})();
