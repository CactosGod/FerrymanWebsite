// Renders products.json into static HTML inside index.html at deploy time,
// so the hats are visible to crawlers and no-JS readers. Runs in the GitHub
// Actions workflow only — the source index.html keeps its <noscript> marker.
// Keep the markup and placement logic in sync with renderHats() in script.js.
import { readFileSync, writeFileSync } from 'node:fs';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const items = JSON.parse(readFileSync('products.json', 'utf8'));

let col = 1; // next free start column for a standard card: 1 or 5
const cards = items.map(p => {
  const sizeClass = p.size === 'large' ? ' hat-card-large' : p.size === 'wide' ? ' hat-card-wide' : '';
  let place;
  if (p.size === 'wide') { place = '1 / span 12'; col = 1; }
  else if (p.size === 'large') { place = '1 / span 8'; col = 1; }
  else { if (col > 5) col = 1; place = `${col} / span 4`; col += 4; }
  const price = p.sold
    ? '<span class="hat-price sold">Sold out</span>'
    : (p.price ? `<span class="hat-price">${esc(p.price)}</span>` : '');
  return `
      <article class="hat-card${sizeClass}" style="--col:${place}">
        <div class="hat-photo">
          <img src="${esc(p.image)}" alt="${esc(p.name)} — ${esc(p.desc)}" loading="lazy" />
        </div>
        <div class="hat-info">
          <div class="hat-title"><h3>${esc(p.name)}</h3>${price}</div>
          <p>${esc(p.desc)}</p>
          <span class="hat-tag">${esc(p.tag)}</span>
        </div>
      </article>`;
}).join('');

const MARKER = '<noscript><p>Enable JavaScript to see the hats.</p></noscript>';
const file = process.argv[2] || 'index.html';
const html = readFileSync(file, 'utf8');
if (!html.includes(MARKER)) {
  console.error(`Gallery marker not found in ${file} — nothing rendered.`);
  process.exit(1);
}
writeFileSync(file, html.replace(MARKER, cards.trim()));
console.log(`Rendered ${items.length} hat cards into ${file}`);
