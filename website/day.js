// day.js (v5)
(function () {
  const $ = (sel) => document.querySelector(sel);

  function getParam(name) {
    const u = new URL(location.href);
    return u.searchParams.get(name);
  }

  async function fetchJSON(url) {
    console.log("[day.js] Fetching:", url);
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      const err = new Error(`HTTP ${res.status} for ${url}`);
      err.body = txt.slice(0, 200);
      throw err;
    }
    return res.json();
  }

  async function tryFetchChain(urls) {
    let lastErr;
    for (const url of urls) {
      try {
        console.log("[day.js] trying url:", url);
        const data = await fetchJSON(url);
        console.log("[day.js] success:", url);
        return data;
      } catch (e) {
        lastErr = e;
        console.warn("[day.js] failed:", url, e, e.body || "");
      }
    }
    throw lastErr;
  }

  async function loadDay() {
    const date = getParam("id");
    if (!date) {
      $("#headline").textContent = "📄 Daily Summary";
      $("#articles").textContent = "No date provided.";
      return;
    }

    $("#headline").textContent = `📄 Summary for ${date}`;

    const base = (window.BASE_URL || "").replace(/\/+$/, "");
    const urls = [
      ...(base ? [`${base}/${encodeURIComponent(date)}.json`] : []),
      ...(base ? [`${base}/website/data/${encodeURIComponent(date)}.json`] : []),
      `./data/${encodeURIComponent(date)}.json`
    ];

    try {
      const data = await tryFetchChain(urls);

      const topics = data?.topics || [];
      if (!topics.length) {
        $("#articles").textContent = "No topics for this day.";
        return;
      }

      $("#articles").innerHTML = topics.map((t) => {
        const links = (t.resources || []).slice(0, 10).map(
          (u) => `<li><a href="${u}" target="_blank" rel="noopener noreferrer">${u}</a></li>`
        ).join("");
        return `
          <section class="topic">
            <h2>${t.name ?? ""}</h2>
            <div>${t.summary ?? "No summary available."}</div>
            ${links ? `<ul>${links}</ul>` : ""}
            <hr/>
          </section>
        `;
      }).join("");

    } catch (e) {
      console.error("[day.js] All fetch attempts failed.", e, e.body || "");
      $("#articles").innerHTML = `
        <div style="color:#b00">
          <strong>Could not load the day's summary.</strong><br/>
          <small>BASE_URL: ${window.BASE_URL || "(unset)"}<br/>
          Tried:<br/>${urls.map(u => `<div>${u}</div>`).join("")}</small>
        </div>
      `;
    }
  }

  document.addEventListener("DOMContentLoaded", loadDay);
})();
