// Scripts for the website. Jupyter Book adds each JS file in _static/ to every page of the book, also to pages
// that are added later. Two parts: collapsible sections (below), and the update check (at the end).
//
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
