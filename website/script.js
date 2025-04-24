fetch('./data/index.json')
  .then(res => res.json())
  .then(days => {
    days.reverse().forEach(date => {
      fetch(`./data/${date}.json`)
        .then(res => res.json())
        .then(data => {
          const div = document.createElement("div");

          const topicList = data.topics || [];
          const summary = topicList[0]?.summary || "No summary available";

          div.innerHTML = `
            <a href="day.html?id=${date}">
              <strong>${date}</strong> [ ${summary.slice(0, 70)}... ]
            </a>
            <hr />
          `;

          document.getElementById("days-list").appendChild(div);
        })
        .catch(err => {
          console.warn(`❌ Could not load ${date}.json:`, err);
        });
    });
  })
  .catch(err => {
    console.error("❌ Failed to load index.json:", err);
  });
