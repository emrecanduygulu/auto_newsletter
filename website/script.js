fetch('./data/index.json')
  .then(res => res.json())
  .then(async dates => {
    const today = new Date().toISOString().slice(0, 10);

    const reversedDates = dates.slice().reverse();

    const summaries = await Promise.all(
      reversedDates.map(async date => {
        try {
          const res = await fetch(`./data/${date}.json`);
          const data = await res.json();
          const topicList = data.topics || [];
          const summary = topicList[0]?.summary || "No summary available";
          return { date, summary };
        } catch (err) {
          console.warn(`❌ Could not load ${date}.json:`, err);
          return null;
        }
      })
    );

    summaries
      .filter(Boolean) // remove nulls from failed fetches
      .forEach(({ date, summary }) => {
        const div = document.createElement("div");
        const isToday = date === today;

        div.innerHTML = `
          <a href="day.html?id=${date}">
            ${isToday ? "🆕 " : ""}<strong>${date}</strong> [ ${summary.slice(0, 70)}... ]
          </a>
          <hr />
        `;

        document.getElementById("days-list").appendChild(div);
      });
  })
  .catch(err => {
    console.error("❌ Failed to load index.json:", err);
  });
