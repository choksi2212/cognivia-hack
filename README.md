# SITARA

**An Agentic Situational Risk Intelligence Platform for Women's Safety in India**

## 🌟 Overview

SITARA is not a panic-response app. It is an agentic situational intelligence system designed to help women make safer decisions before risk escalates — grounded in Indian urban realities, ethical AI principles, and practical deployability.

## 🎯 Key Features

- **Preventive Risk Awareness**: Continuous situational risk evaluation
- **Route-Based Intelligence**: Suggests safer paths before risk escalates
- **Agentic Decision Layer**: Smart, proportional interventions
- **Privacy-First**: No surveillance, user owns their data
- **India-Specific**: Designed for Indian urban environments

## 🏗️ Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Leaflet
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL + Prisma
- **ML**: Random Forest Classifier for risk estimation
- **Agent**: Finite State Machine for decision-making

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL 14+

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 📊 Data Sources

- OpenStreetMap (OSM) for spatial context
- Indian Crime Datasets (Kaggle)
- Crime in India (NCRB)
- OpenCity datasets

## 🛡️ Privacy & Ethics

- No camera or microphone usage
- No face recognition
- No offender profiling
- Models places, not people
- User-controlled escalation

## 📝 License

MIT License

---

Built for women's safety in India 🇮🇳
