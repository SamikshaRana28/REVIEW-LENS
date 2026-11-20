import pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("data/reviews.csv").dropna(subset=["text", "rating"])

def to_label(r):
    if r >= 4: return "positive"
    if r <= 2: return "negative"
    return "neutral"

df["label"] = df["rating"].apply(to_label)

# class balance (nahi toh model sirf "positive" bolega)
n = min(df["label"].value_counts().min(), 20000)
df = df.groupby("label").sample(n=n, random_state=42)

# 70 / 15 / 15 split
X_train, X_temp, y_train, y_temp = train_test_split(
    df["text"], df["label"], test_size=0.3, random_state=42, stratify=df["label"])
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

models = {
    "logreg": LogisticRegression(max_iter=1000),
    "naive_bayes": MultinomialNB(),
    "svm": LinearSVC(),
}

best_name, best_score, best_pipe = None, 0, None
for name, clf in models.items():
    pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), max_features=50000), clf)
    pipe.fit(X_train, y_train)
    score = pipe.score(X_val, y_val)
    print(name, "val accuracy:", round(score, 4))
    if score > best_score:
        best_name, best_score, best_pipe = name, score, pipe

print("Best:", best_name)
pred = best_pipe.predict(X_test)
print(classification_report(y_test, pred))
print(confusion_matrix(y_test, pred))

# final model: Logistic Regression (predict_proba chahiye)
final_pipe = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), max_features=50000),
    LogisticRegression(max_iter=1000)
)
final_pipe.fit(X_train, y_train)
print("LogReg test accuracy:", round(final_pipe.score(X_test, y_test), 4))

joblib.dump(final_pipe, "ml/sentiment.joblib")
print("Saved ml/sentiment.joblib")