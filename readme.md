# ReviewLens

AI-powered Chrome extension that analyses customer reviews on an Amazon product page and shows a short, balanced buying assessment: overall sentiment, what customers like, what they complain about, and possible red flags.

> Status: working prototype (v1). Supports **amazon.in** product pages.

## What it does

When you open a supported product page, ReviewLens:

1. Reads the customer reviews that are visible on the page.
2. Classifies sentiment using a trained ML model combined with the star ratings.
3. Finds product aspects (for example bass, battery, fit, quality) and the sentiment for each one.
4. Flags repeated complaints (for example "stopped working") as possible red flags.
5. Compares the displayed star rating with what the written reviews say.
6. Shows a small card on the page with a verdict, strengths, weaknesses and the number of reviews analysed.

## How it works
Amazon product page
   -> Content script (extension/content.js): scrolls to load reviews, extracts text and ratings
   -> Background script: sends them to the backend
   -> FastAPI backend (backend/main.py)
   -> ML pipeline (ml/analyze.py, ml/aspects.py)
        - sentiment: TF-IDF + scikit-learn model (ml/sentiment.joblib)
        - aspects: universal aspects + product-specific aspects discovered from the reviews
        - sentence/clause-level sentiment per aspect
        - complaint phrase detection and rating-vs-review mismatch
   -> Result card rendered on the product page

Aspects are not tied to one product category. A small universal list (quality, price, delivery, fit...) applies to every product, and product-specific aspects are discovered from nouns that repeat across several reviews. An aspect is shown only when it appears in enough different reviews.

## Tech stack

- Python, FastAPI, Uvicorn
- scikit-learn, TF-IDF, NLTK, pandas, NumPy
- JavaScript, Chrome Extension Manifest V3

## Project structure
ReviewLens/
├── extension/    Chrome extension (manifest.json, content.js, background.js)
├── backend/      FastAPI app (main.py)
├── ml/           analysis code (analyze.py, aspects.py) and the trained model (sentiment.joblib)
├── requirements.txt
└── README.md

## Setup

### 1. Backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python -m nltk.downloader averaged_perceptron_tagger_eng averaged_perceptron_tagger
```

Run it from the **project root**:

```bash
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs to confirm it is running.

### 2. Extension

1. Open `chrome://extensions`.
2. Turn on **Developer mode**.
3. Click **Load unpacked** and select the `extension` folder.
4. Open an Amazon India product page and refresh it. The ReviewLens card appears on the right.

After changing extension code, click **Reload** on the extension and refresh the product page.

## Model

- Task: sentiment classification (positive / negative / neutral)
- Features: TF-IDF
- Model: add your final model here (Logistic Regression / Naive Bayes / SVM)
- Dataset: add dataset name and size here
- Results: add precision, recall, F1 and a confusion matrix here

## Limitations

- Only the reviews visible on the product page are analysed (usually about 8 to 13). The card always shows how many reviews were analysed. This sample does not represent every customer.
- Only amazon.in is supported. Page structure changes can break extraction.
- Reviews written in Hinglish (Hindi in English letters) are understood less well by the English-trained model.
- Aspect discovery is noun-based and can occasionally pick up a generic word.
- Suspicious-pattern signals are hints, not proof that a review is fake.

## Roadmap

- Personalised insights based on what the user cares about
- Two-product comparison
- Flipkart support
- Transformer model (DistilBERT) compared against the classical models
- Hinglish support
