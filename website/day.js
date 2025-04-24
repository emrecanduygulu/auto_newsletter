function getQueryParam(key) {
  const params = new URLSearchParams(window.location.search);
  return params.get(key);
}

const date = getQueryParam("id");
document.getElementById("headline").textContent = `📄 Summary for ${date}`;

fetch(`./data/${date}.json`)
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("articles");

    data.topics.forEach(topic => {
      const section = document.createElement("div");
      section.className = "topic-block";

      const links = topic.resources.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join("");

      section.innerHTML = `
        <h2>🏷️ ${topic.name}</h2>
        ${topic.image ? `<img src="${topic.image}" alt="${topic.name}" class="topic-img" />` : ""}
        <p>${topic.summary}</p>
        <ul>${links}</ul>
        <hr/>
      `;

      container.appendChild(section);
    });
  })
  .catch(err => {
    console.error("❌ Error loading day data:", err);
    document.getElementById("articles").innerHTML = "<p>Could not load the day's summary.</p>";
  });