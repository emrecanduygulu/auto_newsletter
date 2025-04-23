const container = document.getElementById("days-list");

fetch('./data/index.json')
  .then(res => res.json())
  .then(days => {
    days.reverse().forEach(date => {
      fetch(`./data/${date}.json`)
        .then(res => res.json())
        .then(data => {
          const div = document.createElement("div");
          div.className = "day-summary";

          const firstSummary = data.topics?.[0]?.summary || "No summary available";

          div.innerHTML = `
            <a href="day.html?id=${date}">
              <strong>${date}</strong> [ ${firstSummary.slice(0, 70)}... ]
            </a>
            <hr />
          `;

          container.appendChild(div);
        })
        .catch(err => console.warn(`Failed to load ${date}`, err));
    });
  })
  .catch(err => console.error("Couldn't load index.json", err));


  