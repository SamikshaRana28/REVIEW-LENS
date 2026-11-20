import joblib
from collections import defaultdict
from ml.aspects import split_sentences, find_aspects

model = joblib.load("ml/sentiment.joblib")

COMPLAINTS = ["stopped working", "not working", "defective", "fake", "damaged",
              "waste of money", "overheating", "refund", "poor quality", "stopped charging"]

def analyze(reviews, avg_rating):
    texts = [r["text"] for r in reviews]
    n = len(texts)
    if n == 0:
        return {"error": "No reviews found on this page", "analyzed": 0}

    labels = list(model.predict(texts))
    pos = labels.count("positive") / n
    neg = labels.count("negative") / n

    # aspect-wise sentiment
    aspect_votes = defaultdict(list)
    for t in texts:
        for sent in split_sentences(t):
            for a in find_aspects(sent):
                aspect_votes[a].append(model.predict([sent])[0])

    strengths, weaknesses = [], []
    for a, votes in aspect_votes.items():
        if len(votes) < 2:        # bahut kam evidence
            continue
        p = votes.count("positive") / len(votes)
        ng = votes.count("negative") / len(votes)
        if p >= 0.6: strengths.append(a)
        elif ng >= 0.4: weaknesses.append(a)

    # red flags: kitne reviews mein complaint phrase aaya
    flags = []
    for phrase in COMPLAINTS:
        c = sum(1 for t in texts if phrase in t.lower())
        if c >= max(2, 0.15 * n):
            flags.append({"issue": phrase, "mentions": c})

    # rating vs review mismatch
    mismatch = bool(avg_rating and avg_rating >= 4.0 and neg >= 0.30)

    score = pos - neg
    verdict = "Worth buying" if score > 0.5 else "Worth considering" if score > 0.1 else "Be careful"

    summary = f"Based on {n} analysed reviews, {round(pos*100)}% are positive."
    if strengths: summary += " Customers appreciate: " + ", ".join(strengths) + "."
    if weaknesses: summary += " Common concerns: " + ", ".join(weaknesses) + "."
    if mismatch: summary += " Note: the star rating looks higher than the written reviews suggest."

    return {"analyzed": n, "positive_pct": round(pos*100), "negative_pct": round(neg*100),
            "strengths": strengths, "weaknesses": weaknesses, "red_flags": flags,
            "mismatch": mismatch, "verdict": verdict, "summary": summary}