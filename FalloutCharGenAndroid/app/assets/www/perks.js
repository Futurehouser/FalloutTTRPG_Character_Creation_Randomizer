// Random Fallout 76 perk, fetched live from fallout.wiki (nothing from the wiki is bundled in the app).
// The last successful download is cached so the feature still works offline.

const PERKS_PAGE = "https://fallout.wiki/wiki/Fallout_76_Perks";
const PERKS_API = "https://fallout.wiki/api.php?action=parse&page=Fallout_76_Perks&prop=text&format=json&formatversion=2&origin=*";
let PERKS = null;

function parsePerks(html) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const out = [];
  let group = "", special = "";
  const clean = el => el.textContent.replace(/\[edit\]/g, "").replace(/\s+/g, " ").trim();
  doc.querySelectorAll("h2, h3, table").forEach(el => {
    if (el.tagName === "H2") { group = clean(el); return; }
    if (el.tagName === "H3") { special = clean(el); return; }
    if (!el.classList.contains("ace-table")) return;
    if (!/Regular|Ghoul/i.test(group)) return;
    let cur = null;
    el.querySelectorAll("tr").forEach(tr => {
      const tds = [...tr.children].filter(c => c.tagName === "TD");
      if (!tds.length) return;
      const img = tds[0].querySelector("img");
      if (img && tds.length >= 5) {
        let src = img.getAttribute("src") || "";
        if (src.startsWith("//")) src = "https:" + src;
        const a = tds[1].querySelector("a");
        cur = {
          name: clean(tds[1]),
          special,
          group: /Ghoul/i.test(group) ? "Ghoul" : "Regular",
          level: clean(tds[2]),
          image: src.replace(/\/\d+px-/, "/300px-"),
          thumb: src,
          link: a ? "https://fallout.wiki" + a.getAttribute("href") : PERKS_PAGE,
          ranks: [{ rank: clean(tds[3]), desc: clean(tds[4]) }],
        };
        out.push(cur);
      } else if (cur && tds.length >= 2 && !tds[0].querySelector("img")) {
        cur.ranks.push({ rank: clean(tds[0]), desc: clean(tds[1]) });
      }
    });
  });
  return out.filter(p => p.name && p.ranks[0].desc);
}

// returns { perks, source: "online" | "cache" }
async function loadPerks() {
  if (PERKS) return { perks: PERKS, source: "online" };
  try {
    const r = await fetch(PERKS_API, { cache: "no-store" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    const perks = parsePerks(j.parse.text);
    if (!perks.length) throw new Error("the wiki page layout has changed");
    PERKS = perks;
    Platform.saveJSON("perks_cache", { t: Date.now(), perks });
    return { perks, source: "online" };
  } catch (e) {
    const c = await Platform.loadJSON("perks_cache", null);
    if (c && c.perks && c.perks.length) {
      PERKS = c.perks;
      return { perks: PERKS, source: "cache" };
    }
    throw new Error("Couldn't reach fallout.wiki (" + e.message + "). Check the internet connection.");
  }
}
