# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

# -------------------------------
# Step 1: Load the dataset
# -------------------------------
df = pd.read_csv("training_dataset.csv")

# Inspect
print("First 5 rows:")
print(df.head())
print("\nCategory counts:")
print(df['merchant_category'].value_counts())

# -------------------------------
# Step 2: Preprocess the data
# -------------------------------
df['merchant'] = df['merchant'].str.lower().str.strip()

X = df['merchant']           # input features
y = df['merchant_category']  # labels

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# Step 3: Build the ML pipeline
# -------------------------------
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),  # ensures rare words are included
    ("clf", LogisticRegression(max_iter=1000))
])

# -------------------------------
# Step 4: Train the model
# -------------------------------
model.fit(X_train, y_train)
print("\nModel training complete!")

# -------------------------------
# Step 5: Evaluate the model
# -------------------------------
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -------------------------------
# Step 6: Save the trained model
# -------------------------------
joblib.dump(model, "merchant_model.pkl")
print("\nModel saved as 'merchant_model.pkl'!")

# -------------------------------
# Step 7: Test with custom inputs and confidence
# -------------------------------
test_merchants = ["SHELL OIL BLOOMINGDALE IL", "whole foods", "taco bell", "steam", "university bookstore"]
threshold = 0.6  # confidence threshold

print("\nCustom Predictions with Confidence:")
for merchant in test_merchants:
    merchant_clean = merchant.lower().strip()
    probs = model.predict_proba([merchant_clean])[0]  # probability for each class
    max_prob = probs.max()                             # confidence of prediction
    pred = model.classes_[probs.argmax()]             # predicted category
    
    if max_prob < threshold:
        print(f"{merchant} → {pred} (LOW CONFIDENCE: {max_prob:.2f})")
    else:
        print(f"{merchant} → {pred} (Confidence: {max_prob:.2f})")
