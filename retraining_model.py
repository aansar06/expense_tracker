import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

# -------------------------------
# Step 1: Load the dataset from SQLite
# -------------------------------
conn = sqlite3.connect("transactions.db")

# assuming your table is called 'training_dataset'
df = pd.read_sql_query("SELECT merchant, merchant_category FROM training_dataset", conn)
conn.close()

# Inspect
print("First 5 rows:")
print(df.head())
print("\nCategory counts:")
print(df['merchant_category'].value_counts())

# -------------------------------
# Step 2: Preprocess the data
# -------------------------------
df['merchant'] = (
    df['merchant']
      .str.lower()
      .str.strip()
      .str.replace(r'\.com|\.net|\.org|\.co|\.in|\.ca|\.uk', '', regex=True)
)

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
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),  # include unigrams and bigrams
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
