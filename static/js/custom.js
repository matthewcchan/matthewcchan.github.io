// Scroll-to-top button
(function () {
  var btn = document.getElementById("topButton");
  if (!btn) return;

  window.addEventListener("scroll", function () {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
      btn.style.display = "block";
    } else {
      btn.style.display = "none";
    }
  });

  btn.addEventListener("click", function () {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  });
})();

// Publication filter — multi-select, two independent groups (AND between groups, OR within)
(function () {
  const allBtn     = document.getElementById("filter-all");
  const pubCards   = document.querySelectorAll(".pub-card");
  const bookSection = document.getElementById("book-chapter-section");

  if (!allBtn) return;

  // One Set per filter row, keyed by data-filter-row value
  const active = { topic: new Set(), institution: new Set() };

  // Returns true if a card should be visible given current active sets
  function cardMatches(card) {
    const tags = (card.getAttribute("data-tags") || "").split(" ");
    const topicOk  = active.topic.size === 0       || [...active.topic].some(t => tags.includes(t));
    const instOk   = active.institution.size === 0  || [...active.institution].some(t => tags.includes(t));
    return topicOk && instOk;
  }

  // Animate a card into view (expand wrapper, fade card in)
  function showCard(card) {
    card.closest(".pub-card-wrapper").classList.remove("pub-card-hidden");
    card.dataset.visible = "true";
  }

  // Animate a card out of view (collapse wrapper, fade card out)
  function hideCard(card) {
    card.closest(".pub-card-wrapper").classList.add("pub-card-hidden");
    card.dataset.visible = "false";
  }

  function updateCards() {
    pubCards.forEach(function (card) {
      const show      = cardMatches(card);
      const isVisible = card.dataset.visible === "true";
      if (show && !isVisible)       showCard(card);
      else if (!show && isVisible)  hideCard(card);
    });

    // Show/hide the whole Book Chapter section
    if (bookSection) {
      const bookCards  = bookSection.querySelectorAll(".pub-card");
      const anyVisible = [...bookCards].some(c => cardMatches(c));
      bookSection.style.display = anyVisible ? "" : "none";
    }

    // Keep "All" active only when nothing else is selected
    const noneActive = active.topic.size === 0 && active.institution.size === 0;
    allBtn.classList.toggle("active", noneActive);
  }

  // Wrap each card in a slide wrapper (+ inner clip div) and initialise as visible
  pubCards.forEach(function (card) {
    var wrapper = document.createElement("div");
    wrapper.className = "pub-card-wrapper";
    var clip = document.createElement("div");
    clip.className = "pub-card-clip";
    card.parentNode.insertBefore(wrapper, card);
    clip.appendChild(card);
    wrapper.appendChild(clip);
    card.dataset.visible = "true";
  });

  // "All" — clear everything
  allBtn.addEventListener("click", function () {
    active.topic.clear();
    active.institution.clear();
    document.querySelectorAll(".filter-btn[data-filter-row]").forEach(function (b) {
      b.classList.remove("active");
    });
    allBtn.classList.add("active");
    updateCards();
  });

  // Topic / institution buttons — toggle on click
  document.querySelectorAll(".filter-btn[data-filter-row]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const row    = btn.getAttribute("data-filter-row");
      const filter = btn.getAttribute("data-filter");
      const set    = active[row];

      if (set.has(filter)) {
        set.delete(filter);
        btn.classList.remove("active");
      } else {
        set.add(filter);
        btn.classList.add("active");
      }

      updateCards();
    });
  });
})();
