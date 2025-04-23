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
      data.articles.forEach((article, index) => {
        const block = document.createElement("div");
        block.className = "article";
        block.innerHTML = `
          <h2>${index + 1}. ${article.title}</h2>
          <p>${article.summary}</p>
          <a href="${article.url}" target="_blank">Read more</a>
          <hr/>
        `;
        container.appendChild(block);
      });
    });
  