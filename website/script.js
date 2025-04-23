const days = [
    "2025-04-21",
    "2025-04-22",
    "2025-04-23"
  ];
  
  const container = document.getElementById("days-list");
  
  days.reverse().forEach(date => {
    fetch(`./data/${date}.json`)
      .then(res => res.json())
      .then(data => {
        const div = document.createElement("div");
        div.className = "day-summary";
  
        div.innerHTML = `
          <a href="day.html?id=${date}">
            <strong>${date}</strong> [ ${data.articles[0].summary.slice(0, 70)}... ]
          </a>
          <hr />
        `;
  
        container.appendChild(div);
      });
  });
  