import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# ---------------- SAMPLE DATA ----------------

data = {
    "length": [20, 50, 80, 120, 200],
    "keyword_match": [1, 2, 3, 4, 5],
    "sentence_count": [1, 2, 3, 4, 6],
    "score": [2, 4, 6, 8, 10]
}

df = pd.DataFrame(data)

# ---------------- FEATURES ----------------

X = df[["length", "keyword_match", "sentence_count"]]
y = df["score"]

# ---------------- MODEL ----------------

model = RandomForestRegressor()
model.fit(X, y)

# ---------------- FEATURE EXTRACTION ----------------

def extract_features(answer, keywords):
    words = answer.split()
    
    length = len(words)
    keyword_match = sum(1 for k in keywords if k.lower() in answer.lower())
    sentence_count = answer.count('.') + answer.count('?')

    return [length, keyword_match, sentence_count]

# ---------------- PREDICTION FUNCTION ----------------

def score_answer(answer, keywords):
    features = extract_features(answer, keywords)

    feature_names = ["length", "keyword_match", "sentence_count"]
    input_df = pd.DataFrame([features], columns=feature_names)

    prediction = model.predict(input_df)[0]

    prediction = max(0, min(10, prediction))

    return round(prediction, 2)

# ---------------- TEST ----------------

if __name__ == "__main__":
    answer = "ARTIFICIAL INTELLIGENCE"
    keywords = ["machine learning", "data", "model"]

    score = score_answer(answer, keywords)
    print("Score:", score)