from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, ForeignKey, Boolean, Text, Numeric, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# --- USERS TABLE ---
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="adjuster")  # or admin, analyst, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


# --- CUSTOMERS TABLE ---
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="customer")
    policies = relationship("Policy", back_populates="customer")


# --- POLICIES TABLE ---
class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    policy_type = Column(String(50), nullable=False)
    coverage_amount = Column(Numeric(12, 2), nullable=False)
    premium_amount = Column(Numeric(12, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    customer = relationship("Customer", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")


# --- CLAIMS TABLE ---
class Claim(Base):
    __tablename__ = "claims"

    claim_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.policy_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    claim_amount = Column(Numeric(12, 2), nullable=False)
    claim_type = Column(String(100), nullable=False)
    claim_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    fraud_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    fraud_scores = relationship("FraudScore", back_populates="claim")


# --- FRAUD SCORES TABLE ---
class FraudScore(Base):
    __tablename__ = "fraud_scores"

    score_id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False)
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)  # Low, Medium, High
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="fraud_scores")


# --- INDEXING & CONSTRAINTS (Optional Advanced Indexing Example) ---
Index("idx_claim_customer", Claim.customer_id, Claim.claim_type)
Index("idx_policy_number", Policy.policy_number)
UniqueConstraint("email", name="uq_customer_email")
UniqueConstraint("policy_number", name="uq_policy_number")
UniqueConstraint("username", name="uq_user_username")
