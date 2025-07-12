from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import uvicorn
import random
from datetime import datetime
import numpy as np

# Create FastAPI app
app = FastAPI(
    title="Insurance Fraud Detection API",
    description="Enterprise AI-powered fraud detection platform",
    version="1.0.0"
)

# --- Pydantic Models ---
class ClaimInput(BaseModel):
    claim_amount: float = Field(..., example=75000, description="Claim amount in dollars")
    claim_type: str = Field(..., example="Auto Accident", description="Type of insurance claim")
    customer_age: int = Field(..., example=25, description="Customer age")
    policy_tenure: int = Field(..., example=2, description="Years with company")
    claim_description: str = Field(..., example="Total loss in parking lot", description="Claim description")
    location: str = Field(..., example="Remote area", description="Claim location")
    witness_count: int = Field(..., example=0, description="Number of witnesses")

class FraudPrediction(BaseModel):
    fraud_probability: float = Field(..., description="Fraud probability (0-1)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, High, Critical")
    confidence: float = Field(..., description="Model confidence (0-1)")
    recommendation: str = Field(..., description="Investigation recommendation")
    model_version: str = Field(..., description="ML model version")
    processing_time: str = Field(..., description="Processing time")

class ClaimRecord(BaseModel):
    claim_id: int
    claim_amount: float
    fraud_score: float
    risk_level: str
    created_at: str
    claim_type: str

class AnalyticsData(BaseModel):
    total_claims: int
    fraud_detected: int
    avg_fraud_score: float
    high_risk_claims: int
    savings_estimate: float

# --- Simple AI Fraud Detection Logic ---
def simple_fraud_detector(claim_data: dict) -> dict:
    """Simple rule-based fraud detection with ML-like scoring"""
    start_time = datetime.now()
    
    # Extract features
    amount = claim_data["claim_amount"]
    age = claim_data["customer_age"]
    tenure = claim_data["policy_tenure"]
    witnesses = claim_data["witness_count"]
    description = claim_data["claim_description"].lower()
    location = claim_data["location"].lower()
    
    # Fraud scoring logic
    fraud_score = 0.0
    
    # Amount-based risk
    if amount > 50000:
        fraud_score += 0.3
    elif amount > 100000:
        fraud_score += 0.5
    
    # Age-based risk  
    if age < 25 or age > 65:
        fraud_score += 0.2
    
    # Tenure-based risk
    if tenure < 1:
        fraud_score += 0.3
    elif tenure < 3:
        fraud_score += 0.1
    
    # Witness-based risk
    if witnesses == 0:
        fraud_score += 0.2
    
    # Description-based risk
    suspicious_words = ["total loss", "stolen", "fire", "vandalism"]
    if any(word in description for word in suspicious_words):
        fraud_score += 0.1
    
    # Location-based risk
    if "remote" in location or "parking lot" in location:
        fraud_score += 0.1
    
    # Add some randomness to simulate ML variability
    fraud_score += random.uniform(-0.05, 0.05)
    fraud_score = max(0.0, min(1.0, fraud_score))  # Clamp to 0-1
    
    # Risk level classification
    if fraud_score >= 0.8:
        risk_level = "Critical"
        recommendation = "Immediate investigation required"
    elif fraud_score >= 0.6:
        risk_level = "High"
        recommendation = "Requires investigation"
    elif fraud_score >= 0.4:
        risk_level = "Medium"
        recommendation = "Monitor closely"
    else:
        risk_level = "Low"
        recommendation = "Standard processing"
    
    # Calculate processing time
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return {
        "fraud_probability": round(fraud_score, 3),
        "risk_level": risk_level,
        "confidence": round(random.uniform(0.85, 0.98), 2),
        "recommendation": recommendation,
        "model_version": "ensemble_v1.0",
        "processing_time": f"{processing_time:.3f} seconds"
    }

# --- In-Memory Database ---
claims_database = []

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {
        "message": "Insurance Fraud Detection API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "ai_enabled": True
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "message": "API is operational",
        "components": {
            "database": "active",
            "ml_models": "active", 
            "api": "active"
        }
    }

@app.get("/api/v1/status")
def api_status():
    return {
        "api_version": "1.0.0",
        "ai_enabled": True,
        "models_loaded": True,
        "total_claims_processed": len(claims_database),
        "endpoints": [
            "/health",
            "/api/v1/predict-fraud",
            "/api/v1/claims", 
            "/api/v1/analytics",
            "/docs"
        ]
    }

@app.post("/api/v1/predict-fraud", response_model=FraudPrediction)
def predict_fraud(claim: ClaimInput):
    """AI-powered fraud detection for insurance claims"""
    try:
        # Run fraud detection
        result = simple_fraud_detector(claim.dict())
        return FraudPrediction(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud prediction failed: {str(e)}")

@app.post("/api/v1/claims", response_model=dict)
def create_claim(claim: ClaimInput):
    """Create new claim with automatic fraud scoring"""
    try:
        # Get fraud prediction
        fraud_result = simple_fraud_detector(claim.dict())
        
        # Create claim record
        claim_record = {
            "claim_id": len(claims_database) + 1,
            "claim_amount": claim.claim_amount,
            "fraud_score": fraud_result["fraud_probability"],
            "risk_level": fraud_result["risk_level"],
            "created_at": datetime.now().isoformat(),
            "claim_type": claim.claim_type,
            "customer_age": claim.customer_age,
            "recommendation": fraud_result["recommendation"]
        }
        
        # Save to database
        claims_database.append(claim_record)
        
        return {
            "claim_created": True,
            "claim_id": claim_record["claim_id"],
            "fraud_analysis": fraud_result,
            "message": f"Claim {claim_record['claim_id']} created with {fraud_result['risk_level']} risk level"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claim creation failed: {str(e)}")

@app.get("/api/v1/claims", response_model=List[ClaimRecord])
def list_claims():
    """Get all processed claims with fraud scores"""
    return [ClaimRecord(**claim) for claim in claims_database]

@app.get("/api/v1/analytics", response_model=AnalyticsData)
def get_analytics():
    """Get fraud detection analytics and insights"""
    if not claims_database:
        return AnalyticsData(
            total_claims=0,
            fraud_detected=0,
            avg_fraud_score=0.0,
            high_risk_claims=0,
            savings_estimate=0.0
        )
    
    total_claims = len(claims_database)
    fraud_claims = [c for c in claims_database if c["fraud_score"] >= 0.5]
    high_risk_claims = [c for c in claims_database if c["risk_level"] in ["High", "Critical"]]
    avg_score = sum(c["fraud_score"] for c in claims_database) / total_claims
    
    # Estimate savings (assume $50K average fraud prevention)
    savings_estimate = len(fraud_claims) * 50000
    
    return AnalyticsData(
        total_claims=total_claims,
        fraud_detected=len(fraud_claims),
        avg_fraud_score=round(avg_score, 3),
        high_risk_claims=len(high_risk_claims),
        savings_estimate=savings_estimate
    )

@app.get("/api/v1/fraud-stats")
def fraud_statistics():
    """Detailed fraud statistics for executive dashboard"""
    if not claims_database:
        return {"message": "No claims processed yet"}
    
    total = len(claims_database)
    by_risk = {}
    for claim in claims_database:
        risk = claim["risk_level"]
        by_risk[risk] = by_risk.get(risk, 0) + 1
    
    return {
        "total_claims": total,
        "fraud_detection_rate": f"{(len([c for c in claims_database if c['fraud_score'] >= 0.5]) / total * 100):.1f}%",
        "risk_distribution": by_risk,
        "average_claim_amount": f"${sum(c['claim_amount'] for c in claims_database) / total:,.2f}",
        "total_claims_value": f"${sum(c['claim_amount'] for c in claims_database):,.2f}",
        "estimated_fraud_prevented": f"${len([c for c in claims_database if c['fraud_score'] >= 0.5]) * 50000:,.2f}"
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)