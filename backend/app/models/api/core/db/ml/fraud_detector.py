# fraud_detector.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
from datetime import datetime

class FraudDetector:
    def __init__(self):
        self.models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "xgboost": XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
            "neural_net": MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=300)
        }
        self.ensemble_weights = {
            "random_forest": 0.4,
            "xgboost": 0.4,
            "neural_net": 0.2
        }
        self.scaler = StandardScaler()
        self.fitted = False

    def generate_synthetic_data(self, n_samples=10000):
        np.random.seed(42)
        data = pd.DataFrame({
            "claim_amount": np.random.exponential(scale=5000, size=n_samples),
            "claim_type": np.random.randint(0, 5, size=n_samples),
            "customer_history": np.random.poisson(2, size=n_samples),
            "claim_hour": np.random.randint(0, 24, size=n_samples),
            "risk_region": np.random.randint(0, 3, size=n_samples),
            "policy_age_months": np.random.randint(1, 240, size=n_samples),
            "documentation_flag": np.random.randint(0, 2, size=n_samples),
            "is_fraud": np.random.binomial(1, 0.1, size=n_samples)
        })
        return data

    def feature_engineering(self, df):
        df = df.copy()
        df["amount_per_history"] = df["claim_amount"] / (df["customer_history"] + 1)
        df["hour_risk"] = df["claim_hour"].apply(lambda x: 1 if x in [0, 1, 2, 3] else 0)
        return df

    def train_models(self, df):
        df = self.feature_engineering(df)
        X = df.drop("is_fraud", axis=1)
        y = df["is_fraud"]
        X_scaled = self.scaler.fit_transform(X)

        for name, model in self.models.items():
            scores = cross_val_score(model, X_scaled, y, cv=5, scoring="roc_auc")
            print(f"{name} AUC: {scores.mean():.4f}")
            model.fit(X_scaled, y)
            dump(model, f"models/{name}.joblib")

        dump(self.scaler, "models/scaler.joblib")
        self.fitted = True

    def load_models(self):
        self.models = {
            "random_forest": load("models/random_forest.joblib"),
            "xgboost": load("models/xgboost.joblib"),
            "neural_net": load("models/neural_net.joblib")
        }
        self.scaler = load("models/scaler.joblib")
        self.fitted = True

    def predict_fraud(self, claim_data):
        if not self.fitted:
            self.load_models()

        df = pd.DataFrame([claim_data])
        df = self.feature_engineering(df)
        X_scaled = self.scaler.transform(df)

        weighted_probs = 0
        for name, model in self.models.items():
            prob = model.predict_proba(X_scaled)[:, 1]
            weighted_probs += prob * self.ensemble_weights[name]

        fraud_prob = float(weighted_probs[0])
        risk_level = self.get_risk_level(fraud_prob)

        return {
            "fraud_probability": round(fraud_prob, 4),
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_risk_level(self, score):
        if score < 0.3:
            return "Low"
        elif score < 0.6:
            return "Medium"
        elif score < 0.85:
            return "High"
        else:
            return "Critical"

    def evaluate_model(self, df):
        df = self.feature_engineering(df)
        X = df.drop("is_fraud", axis=1)
        y = df["is_fraud"]
        X_scaled = self.scaler.transform(X)

        for name, model in self.models.items():
            y_pred = model.predict(X_scaled)
            print(f"=== {name.upper()} ===")
            print(classification_report(y, y_pred))
            print("AUC:", roc_auc_score(y, model.predict_proba(X_scaled)[:, 1]))
