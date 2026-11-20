import re

ASPECTS = {
    "battery": ["battery", "charging", "charge", "backup", "drain", "mah"],
    "camera": ["camera", "photo", "picture", "video", "selfie", "lens"],
    "display": ["display", "screen", "brightness", "amoled", "resolution"],
    "performance": ["performance", "speed", "lag", "hang", "processor", "gaming"],
    "build": ["build", "quality", "design", "plastic", "durable", "broke"],
    "heating": ["heat", "heating", "overheat", "warm"],
    "price": ["price", "value", "worth", "costly", "expensive"],
}

def split_sentences(text):
    return [s.strip() for s in re.split(r"[.!?\n]+", text) if len(s.strip()) > 3]

def find_aspects(sentence):
    s = sentence.lower()
    return [a for a, words in ASPECTS.items() if any(w in s for w in words)]