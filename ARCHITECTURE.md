insurance-fraud-platform/
│
├── backend/                     # FastAPI app with ML logic
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── core/                # Settings, configs, utilities
│   │   ├── db/                  # Database models & session
│   │   ├── models/              # ML models & logic
│   │   ├── services/            # Business logic (fraud scoring, etc.)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── security/            # Auth, tokens, passwords
│   │   └── main.py              # FastAPI app entry point
│   └── Dockerfile
│
├── frontend/                    # React admin dashboard
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/            # API calls
│   │   ├── utils/
│   │   ├── assets/
│   │   └── App.tsx
│   └── Dockerfile
│
├── database/
│   ├── init.sql                 # Schema for insurance claims
│   └── seed_data.sql           # Sample fraud/legit claim data
│
├── .env                         # Environment config
├── docker-compose.yml          # Multi-container setup
├── README.md                    # Documentation
└── docs/                        # API & platform docs
