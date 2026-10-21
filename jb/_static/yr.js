// Scripts for the course's pages (yr/). Jupyter Book adds each JS file in _static/ to every page.
//
// Collapsible sections (yr/chap08_additions.ipynb): a markdown cell that starts with a heading and has
// <div class="yr-collapse"> makes its section collapsible. In Colab, any heading can be collapsed. On the
// website, this script puts the heading and the rest of its section in a <details> block, open at the
// start: a click on the heading hides or shows the section.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('section > div.yr-collapse').forEach((marker) => {
    const section = marker.parentElement;
    const heading = section.querySelector(':scope > h2, :scope > h3, :scope > h4');
    if (!heading) return;
    const box = document.createElement('details');
    box.className = 'yr-collapse';
    box.open = true;
    const summary = document.createElement('summary');
    heading.before(box);
    summary.append(heading);
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
