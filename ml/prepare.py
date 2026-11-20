import pandas as pd

df = pd.read_csv("data/Amazon_Unlocked_Mobile.csv")
print(df.columns.tolist())   # columns ke naam dekhne ke liye

df = df.rename(columns={"Reviews": "text", "Rating": "rating"})
df = df[["text", "rating"]].dropna()
df.to_csv("data/reviews.csv", index=False)

print(len(df), "reviews saved")
print(df["rating"].value_counts())