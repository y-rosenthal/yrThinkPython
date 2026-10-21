// Scripts for the course's pages (yr/). Jupyter Book adds each JS file in _static/ to every page.
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
