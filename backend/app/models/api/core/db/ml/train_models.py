# train_models.py

import os
from pathlib import Path
from fraud_detector import FraudDetector

def main():
    # Ensure model directory exists
    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    print("📊 Initializing fraud detection model training...")

    # Initialize the FraudDetector system
    detector = FraudDetector()

    # Step 1: Generate synthetic training data
    print("🔄 Generating synthetic insurance claims...")
    df = detector.generate_synthetic_data(n_samples=12000)

    print(f"✅ Synthetic dataset created with shape: {df.shape}")
    print(f"🔍 Fraud rate in sample: {df['is_fraud'].mean():.2%}\n")

    # Step 2: Train all models with evaluation
    print("🧠 Training models (Random Forest, XGBoost, Neural Network)...")
    detector.train_models(df)

    # Step 3: Evaluate model performance
    print("\n📈 Evaluating model performance on training set...")
    detector.evaluate_model(df)

    print("\n💾 Models saved in the 'models/' directory.")
    print("🚀 Training pipeline completed successfully.")

if __name__ == "__main__":
    main()
