// ReviewLens content script (Amazon product page)

function getReviews() {
  const out = [];
  const seen = new Set();
  const nodes = document.querySelectorAll(
    '[data-hook="review"], [data-hook="cmps-review"], [id^="customer_review"], .review'
  );
  console.log("ReviewLens: review containers found:", nodes.length);
  nodes.forEach(el => {
    let text = (el.querySelector(
      '[data-hook="review-body"], [data-hook="cmps-review-body"], .review-text-content, .review-text, [class*="review-text"]'
    )?.textContent || "").trim();
    // Fallback: body selector na mile to poore review block ka text lo
    if (!text) {
      text = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
      if (text.length < 40) return;
      console.log("ReviewLens: used fallback text for a review");
    }
    if (text.length < 10 || seen.has(text)) return;
    seen.add(text);
    const starText = el.querySelector('[data-hook*="review-star-rating"], .a-icon-alt')?.textContent || "";
    const rating = parseFloat(starText);
    out.push({ text, rating: isNaN(rating) ? null : rating });
  });
  return out;
}

function getAvgRating() {
  const t = document.querySelector('[data-hook="rating-out-of-text"]')?.textContent
         || document.querySelector('#acrPopover')?.getAttribute("title") || "";
  const v = parseFloat(t);
  return isNaN(v) ? null : v;
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function getCard() {
  let card = document.getElementById("reviewlens-card");
  if (!card) {
    card = document.createElement("div");
    card.id = "reviewlens-card";
    card.style.cssText = `
      position: fixed; top: 80px; right: 20px; width: 320px;
      max-height: 80vh; overflow-y: auto; z-index: 2147483647;
      background: #fff; color: #111; border: 1px solid #ddd;
      border-radius: 12px; padding: 16px;
      box-shadow: 0 4px 20px rgba(0,0,0,.25);
      font: 14px/1.4 system-ui, sans-serif;`;
    document.body.appendChild(card);
  }
  return card;
}

function render(d) {
  const card = getCard();
  if (d.error) {
    card.innerHTML = `<b>ReviewLens</b><p>${escapeHtml(d.error)}</p>`;
    return;
  }
  const strengths = (d.strengths || []).map(escapeHtml).join(", ") || "-";
  const weaknesses = (d.weaknesses || []).map(escapeHtml).join(", ") || "-";
  const flags = (d.red_flags || []).map(f => escapeHtml(f.issue)).join(", ");
  card.innerHTML = `
    <h3 style="margin:0 0 8px">ReviewLens</h3>
    <p><b>${escapeHtml(d.verdict)}</b> · analysed ${escapeHtml(d.analyzed)} reviews</p>
    <p>${escapeHtml(d.summary)}</p>
    <p>👍 ${strengths}</p>
    <p>👎 ${weaknesses}</p>
    ${flags ? `<p>🚩 ${flags}</p>` : ""}
    <small>Based only on reviews visible on this page, not all customers.</small>`;
}

// Reviews lazy-load hote hain, isliye scroll karke wait karte hain
async function waitForReviews(maxAttempts = 12) {
  const startY = window.scrollY;
  for (let i = 1; i <= maxAttempts; i++) {
    const reviews = getReviews();
    console.log("ReviewLens: attempt", i, "found", reviews.length, "reviews");
    if (reviews.length > 0) {
      window.scrollTo(0, startY);
      return reviews;
    }
    const section = document.querySelector("#reviewsMedley, #reviews-medley-footer, #customerReviews, #cm-cr-dp-review-list");
    if (section) section.scrollIntoView();
    else window.scrollBy(0, 800);
    await new Promise(r => setTimeout(r, 1000));
  }
  window.scrollTo(0, startY);
  return [];
}

let started = false;
async function run() {
  if (started) return;
  started = true;

  getCard().innerHTML = "<b>ReviewLens</b><p>Analysing reviews...</p>";

  const reviews = await waitForReviews();
  if (reviews.length === 0) {
    render({ error: "No reviews found on this page" });
    return;
  }

  chrome.runtime.sendMessage(
    {
      type: "ANALYZE",
      payload: {
        title: document.querySelector("#productTitle")?.textContent.trim(),
        avg_rating: getAvgRating(),
        reviews: reviews
      }
    },
    res => {
      console.log("ReviewLens: backend response", res);
      if (chrome.runtime.lastError) {
        render({ error: "Extension error: " + chrome.runtime.lastError.message });
        return;
      }
      render(res?.ok && res.data && !res.data.error
        ? res.data
        : { error: res?.data?.error || "Backend not reachable" });
    }
  );
}

console.log("ReviewLens: content script loaded");
setTimeout(run, 1500);