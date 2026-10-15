const form = document.querySelector('#order-form');
const status = document.querySelector('#form-status');

form?.addEventListener('submit', (event) => {
  event.preventDefault();
  const d = new FormData(form);
  const subject = `Hat enquiry — ${d.get('name') || 'new customer'}`;
  const body = [
    `Name: ${d.get('name') || ''}`,
    `Email: ${d.get('email') || ''}`,
    `Head size: ${d.get('headSize') || '-'}`,
    `Enquiry: ${d.get('enquiry') || '-'}`,
    `Material / colour: ${d.get('material') || '-'}`,
    '',
    d.get('notes') || ''
  ].join('\n');
  window.location.href = `mailto:hats@ferrymanhats.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  status.textContent = 'Your mail app should open with the enquiry — if not, write to hats@ferrymanhats.com.';
  status.classList.add('success');
});

/* ---------- gallery rendered from products.json ---------- */
const grid = document.getElementById('hat-grid');

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderHats(items) {
  grid.innerHTML = items.map(p => {
    const sizeClass = p.size === 'large' ? ' hat-card-large' : p.size === 'wide' ? ' hat-card-wide' : '';
    const price = p.sold
      ? '<span class="hat-price sold">Sold out</span>'
      : (p.price ? `<span class="hat-price">${escapeHtml(p.price)}</span>` : '');
    return `
      <article class="hat-card${sizeClass}">
        <div class="hat-photo">
          <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)} — ${escapeHtml(p.desc)}" loading="lazy" />
        </div>
        <div class="hat-info">
          <div class="hat-title"><h3>${escapeHtml(p.name)}</h3>${price}</div>
          <p>${escapeHtml(p.desc)}</p>
          <span class="hat-tag">${escapeHtml(p.tag)}</span>
        </div>
      </article>`;
  }).join('');
}

if (grid) {
  fetch('products.json', { cache: 'no-store' })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(renderHats)
    .catch(() => {
      grid.innerHTML = '<p style="color:var(--ash);grid-column:span 12">' +
        'Could not load products.json — serve this folder (python3 serve.py) instead of opening the file directly.</p>';
    });
}
