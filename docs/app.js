async function loadModule(container) {
  const src = container.getAttribute("data-source");
  try {
    const res = await fetch(src + "?t=" + Date.now());
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    renderItems(container, data);
  } catch (err) {
    container.innerHTML = `<p class="error">Keine Daten verfügbar (${err.message}). Läuft der Workflow schon?</p>`;
  }
}

function renderItems(container, data) {
  const items = data.items || [];
  if (items.length === 0) {
    container.innerHTML = '<p class="empty">Noch keine Einträge.</p>';
    return;
  }

  const updated = data.last_updated
    ? new Date(data.last_updated).toLocaleString("de-DE")
    : "unbekannt";

  const rows = items.slice(0, 25).map((item) => {
    const critClass = item.critical ? " critical" : "";
    const title = item.title || item.topic || "Ohne Titel";
    const link = item.link || "#";
    const metaParts = [];
    if (item.category) metaParts.push(item.category);
    if (item.source) metaParts.push(item.source);
    if (item.published) metaParts.push(item.published);
    if (item.cvss_score) metaParts.push("CVSS " + item.cvss_score);
    if (item.status) metaParts.push(item.status);

    return `<div class="item${critClass}">
      <a href="${link}" target="_blank" rel="noopener">${escapeHtml(title)}</a>
      <div class="meta">${escapeHtml(metaParts.join(" · "))}</div>
    </div>`;
  }).join("");

  container.innerHTML = `<p class="meta">Zuletzt aktualisiert: ${updated}</p>${rows}`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

document.querySelectorAll(".list").forEach(loadModule);
