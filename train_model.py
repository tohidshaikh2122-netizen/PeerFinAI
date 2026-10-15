import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# Create sample financial data
np.random.seed(42)

data = pd.DataFrame({
    "income": np.random.randint(10000, 80000, 1000),
    "loan": np.random.randint(5000, 50000, 1000),
    "debt": np.random.randint(0, 30000, 1000),
    "late_payments": np.random.randint(0, 6, 1000)
})

# Create demo risk labels
risk = (
    (data["loan"] / data["income"])
    + (data["debt"] / data["income"])
    + data["late_payments"] * 0.25
)

data["high_risk"] = (risk > 2).astype(int)

# Train the AI model
X = data[["income", "loan", "debt", "late_payments"]]
y = data["high_risk"]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# Save the trained model
model_folder = Path("models")
model_folder.mkdir(exist_ok=True)

with open(model_folder / "risk_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("AI model trained successfully!")
print("Model saved in models/risk_model.pkl")