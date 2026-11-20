"""Aspect helpers for ReviewLens.

Works for any product category:
1. UNIVERSAL aspects (quality, price, delivery...) apply to every product.
2. discover_aspects() finds product-specific aspects (bass, battery, fabric,
   camera...) from the reviews themselves, so no hand-made list per category.
"""
import math
import re
from collections import Counter

try:
    import nltk
except ImportError:  # works without nltk too, just less precise
    nltk = None

UNIVERSAL = {
    "quality":      ["quality", "build", "material", "durable", "durability", "sturdy", "flimsy", "cheap"],
    "price/value":  ["price", "value", "worth", "money", "expensive", "budget", "overpriced"],
    "delivery":     ["delivery", "delivered", "shipping", "courier"],
    "packaging":    ["packaging", "packed", "packing"],
    "size/fit":     ["size", "fit", "fitting", "tight", "loose"],
    "design/looks": ["design", "looks", "look", "colour", "color", "style"],
    "service":      ["service", "support", "replacement", "refund", "warranty"],
    "authenticity": ["fake", "duplicate", "genuine", "counterfeit", "original"],
}

STOP = set("""
the and for with this that was were are but not you your have has had its it's they them their there
from into out very just also too than then when what which while would could should about after
before because been being over under only some such other more most much many really good bad best
great nice awesome excellent amazing worst better well like love hate happy sad okay ok fine super
product item thing things order ordered day days time month months week weeks year years one two three
use used using buy bought buying amazon seller review reviews rupee rupees bit lot everything something
anything nothing way get got give gave take took make made want wanted need needed come came go went
look looks looking see seen say said tell told think thought know knew feel felt try tried work works
worked working rating star stars person people guy guys sir mam madam thank thanks please overall
""".split())


def split_sentences(text):
    """Split a review into sentences and clauses ('X is good but Y is bad' -> 2 parts)."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out = []
    for p in parts:
        for clause in re.split(r"\s+(?:but|however|although|though|while)\s+", p, flags=re.I):
            clause = clause.strip()
            if len(clause) > 3:
                out.append(clause)
    return out


def _has_word(sentence_low, kw):
    return re.search(r"\b" + re.escape(kw), sentence_low) is not None


def find_aspects(sentence, extra_aspects=()):
    """Return the aspects (universal + discovered) mentioned in one sentence."""
    low = sentence.lower()
    found = []
    for name, kws in UNIVERSAL.items():
        if any(_has_word(low, k) for k in kws):
            found.append(name)
    for a in extra_aspects:
        if _has_word(low, a) and a not in found:
            found.append(a)
    return found


def _candidate_nouns(text):
    words = re.findall(r"[A-Za-z]+", text)
    if nltk:
        try:
            tagged = nltk.pos_tag(words)
            return {w.lower() for w, t in tagged if t.startswith("NN") and len(w) > 2}
        except Exception:
            pass  # tagger data missing -> fall back to plain words
    return {w.lower() for w in words if len(w) > 2}


def discover_aspects(texts, top_k=8):
    """Nouns that show up in several different reviews = this product's aspects."""
    n = len(texts)
    min_reviews = max(3, math.ceil(0.15 * n))
    universal_words = {k for kws in UNIVERSAL.values() for k in kws}
    counts = Counter()
    for t in texts:
        counts.update(_candidate_nouns(t))  # a set, so one count per review
    aspects = []
    for w, c in counts.most_common(80):
        if c < min_reviews:
            break
        if w in STOP or w in universal_words or not w.isalpha():
            continue
        aspects.append(w)
        if len(aspects) >= top_k:
            break
    return aspects