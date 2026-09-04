# 🏥 LifeLink AI - Autonomous Emergency Healthcare Backend

FastAPI + Python 3.11+ backend service powering **LifeLink AI**, an AI-driven emergency response healthcare application.

---

## 🎯 System Architecture & Responsibilities

- **Autonomous Emergency Triage**: Receives patient symptom inputs, forwards to the AI Agent (`/agent/triage`), and **autonomously dispatches ambulances** without human latency when severity $\ge 4$.
- **Real-Time Ambulance & Hospital Tracking**: Updates and reads live location & ETA data stored in Firebase Firestore.
- **Firebase Auth Integration**: Token verification and user authentication endpoints.

---

## 🚀 Quick Start (Local Setup)

### 1. Install Dependencies
Ensure Python 3.11+ is installed.
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` as needed:
```env
FIREBASE_CREDENTIALS=firebase_service_account.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FEATHERLESS_API_KEY=your_featherless_key_here
AGENT_BASE_URL=http://localhost:8001
LOG_LEVEL=INFO
PORT=8000
```

### 3. Firebase Console Setup Guide (Step-by-Step)
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Create or select your project (e.g. `lifelink-ai`).
3. Navigate to **Project Settings** $\rightarrow$ **Service accounts**.
4. Click **Generate new private key** and save the JSON file.
5. Place the downloaded JSON file in the project root directory as `firebase_service_account.json`.
6. Enable **Firestore Database** and **Authentication** (Email/Password) in the console.

> 💡 **Note:** If `firebase_service_account.json` is missing during local dev, the backend automatically operates in **Local Mock Fallback Mode** so you can test endpoints immediately without crashing!

### 4. Seed Hospital Sample Data
Populate Firestore with initial sample hospitals (Apollo, Care, KIMS):
```bash
python scripts/seed_data.py
```

### 5. Run Local Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at:
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Automated Tests

Run the test suite with pytest:
```bash
pytest tests/ -v
```

---

## ☁️ Google Cloud Run Deployment

Deploy directly from source without managing Dockerfiles:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy source directly to Cloud Run
gcloud run deploy healthtrack-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FEATHERLESS_API_KEY=your_key,AGENT_BASE_URL=http://your-agent-url

# 3. Retrieve Deployed Endpoint URL
gcloud run services describe healthtrack-backend --region us-central1 --format 'value(status.url)'
```

---

## 🔗 Key API Contracts

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/signup` | Create user account | No |
| `POST` | `/api/v1/auth/login` | Login user & return ID token | No |
| `GET` | `/api/v1/auth/me` | Fetch current authenticated user | Yes |
| `POST` | `/api/v1/triage/emergency` | Symptom triage + Autonomous Ambulance Dispatch | Yes |
| `GET` | `/api/v1/ambulance/{ambulanceId}` | Get ambulance status & ETA | Yes |
| `PUT` | `/api/v1/ambulance/{ambulanceId}/location` | Update live ambulance coordinates | Yes |
| `PUT` | `/api/v1/ambulance/{ambulanceId}/status` | Update ambulance status | Yes |
| `GET` | `/api/v1/hospitals` | List all hospitals & bed availability | Yes |
| `GET` | `/api/v1/hospitals/{hospitalId}` | Hospital detail lookup | Yes |

---

## 📄 License
Built for LifeLink AI Hackathon 2026.
