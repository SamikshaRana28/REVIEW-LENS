import joblib
from collections import defaultdict
from ml.aspects import split_sentences, find_aspects, discover_aspects

model = joblib.load("ml/sentiment.joblib")

COMPLAINTS = [
    "stopped working", "not working", "stopped charging", "defective", "fake", "duplicate",
    "damaged", "waste of money", "overheating", "heating", "refund", "poor quality",
    "bad quality", "disconnect", "not connecting", "peeling", "broke", "broken",
    "used product", "return",
]


def _norm(label):
    s = str(label).lower()
    if s.startswith("pos") or s == "1":
        return "positive"
    if s.startswith("neg") or s == "0":
        return "negative"
    return "neutral"


def _predict(texts):
    return [_norm(x) for x in model.predict(texts)] if texts else []


def analyze(reviews, avg_rating):
    texts = [r["text"] for r in reviews]
    n = len(texts)
    if n == 0:
        return {"error": "No reviews found on this page", "analyzed": 0}

    # ---- overall sentiment: text model + star ratings of the same reviews ----
    labels = _predict(texts)
    model_pos = labels.count("positive") / n
    model_neg = labels.count("negative") / n

    rated = [r["rating"] for r in reviews if r.get("rating")]
    rating_pos = rating_neg = None
    if len(rated) >= n / 2:
        rating_pos = sum(1 for x in rated if x >= 4) / len(rated)
        rating_neg = sum(1 for x in rated if x <= 2) / len(rated)

    if rating_pos is not None:
        pos = (model_pos + rating_pos) / 2
        neg = (model_neg + rating_neg) / 2
    else:
        pos, neg = model_pos, model_neg

    # ---- aspects: universal + discovered from these reviews ----
    extra = discover_aspects(texts)
    items = []  # (review_index, sentence, aspects)
    for i, t in enumerate(texts):
        for sent in split_sentences(t):
            asp = find_aspects(sent, extra)
            if asp:
                items.append((i, sent, asp))

    sent_labels = _predict([s for _, s, _ in items])
    votes = defaultdict(list)      # aspect -> [labels]
    reviews_seen = defaultdict(set)  # aspect -> {review indexes}
    for (i, _, asp), lab in zip(items, sent_labels):
        for a in asp:
            votes[a].append(lab)
            reviews_seen[a].add(i)

    min_evidence = 3 if n >= 10 else 2
    strengths, weaknesses, aspect_details = [], [], {}
    for a, v in votes.items():
        mentions = len(reviews_seen[a])
        if mentions < min_evidence:
            continue
        p = v.count("positive") / len(v)
        ng = v.count("negative") / len(v)
        aspect_details[a] = {"mentions": mentions, "positive_pct": round(p * 100),
                             "negative_pct": round(ng * 100)}
        if p >= 0.6 and p > ng:
            strengths.append((p, mentions, f"{a} ({mentions} reviews, {round(p*100)}% positive)"))
        elif ng >= 0.4:
            weaknesses.append((ng, mentions, f"{a} ({mentions} reviews, {round(ng*100)}% negative)"))

    strengths = [s for _, _, s in sorted(strengths, reverse=True)[:5]]
    weaknesses = [s for _, _, s in sorted(weaknesses, reverse=True)[:5]]

    # ---- red flags: complaint phrases repeated across reviews ----
    flags = []
    for phrase in COMPLAINTS:
        c = sum(1 for t in texts if phrase in t.lower())
        if c >= max(2, 0.15 * n):
            flags.append({"issue": f"{phrase} ({c} reviews)", "mentions": c})

    # ---- rating vs written reviews ----
    mismatch = bool(avg_rating and avg_rating >= 4.0 and model_neg >= 0.30)

    score = pos - neg
    verdict = "Worth buying" if score > 0.5 else "Worth considering" if score > 0.1 else "Be careful"

    summary = f"Based on {n} analysed reviews, about {round(pos*100)}% are positive and {round(neg*100)}% negative."
    if strengths:
        summary += " Customers appreciate: " + ", ".join(s.split(" (")[0] for s in strengths) + "."
    if weaknesses:
        summary += " Common concerns: " + ", ".join(w.split(" (")[0] for w in weaknesses) + "."
    if mismatch:
        summary += " Note: the star rating looks higher than the written reviews suggest."

    return {
        "analyzed": n,
        "positive_pct": round(pos * 100),
        "negative_pct": round(neg * 100),
        "model_positive_pct": round(model_pos * 100),
        "rating_positive_pct": None if rating_pos is None else round(rating_pos * 100),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "red_flags": flags,
        "aspect_details": aspect_details,
        "discovered_aspects": extra,
        "mismatch": mismatch,
        "verdict": verdict,
        "summary": summary,
    }