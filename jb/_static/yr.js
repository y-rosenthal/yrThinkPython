// Scripts for the course's pages (yr/). Jupyter Book adds each JS file in _static/ to every page.
//
// Collapsible sections. In Colab, the reader can collapse any heading. On the website, this script puts a
// heading and the rest of its section in a <details> block, open at the start: a click on the heading hides or
// shows the section.
// - A page with <div class="yr-collapse-all"></div> (in any markdown cell): every section with a ##, ### or
//   #### heading is collapsible, and each of these headings has the buttons "Collapse all" and "Expand all".
//   The buttons change only these sections, not the Answer and "Diving deeper" boxes.
// - On other pages, only a section whose heading cell has <div class="yr-collapse"> is collapsible.
document.addEventListener('DOMContentLoaded', () => {
  const HEADINGS = ':scope > h2, :scope > h3, :scope > h4';
  const all = document.querySelector('div.yr-collapse-all') !== null;
  const sections = all
    ? [...document.querySelectorAll('section')].filter((s) => s.querySelector(HEADINGS))
    : [...document.querySelectorAll('section > div.yr-collapse')].map((marker) => marker.parentElement);

  const setAll = (open) => {
    document.querySelectorAll('details.yr-collapse').forEach((box) => { box.open = open; });
  };
  const button = (text, open, summary) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'yr-toggle-all';
    b.textContent = text;
    b.addEventListener('click', (event) => {
      event.preventDefault();  // a click in a <summary> also opens or closes its <details>: stop that
      event.stopPropagation();
      setAll(open);
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
    if (all) summary.append(button('Collapse all', false, summary), button('Expand all', true, summary));
    box.append(summary);
    while (box.nextSibling) box.append(box.nextSibling);
  });

  // A link to a part of a closed section (for example, from the Contents list) opens the section.
  const openTarget = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = id && document.getElementById(id);
    if (!target) return;
    for (let box = target.closest('details.yr-collapse'); box; box = box.parentElement.closest('details.yr-collapse')) {
      box.open = true;
    }
    target.scrollIntoView();
  };
  window.addEventListener('hashchange', openTarget);
  openTarget();
});
