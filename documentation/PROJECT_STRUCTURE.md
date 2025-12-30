# Project Structure Overview

```
project-fleetflow/
│
├── 📄 START_HERE.md ⭐
│   └─ Read this first! Quick orientation guide
│
├── 📄 README.md
│   └─ Project overview & quick start
│
├── 🚀 Quick Start Guides
│   ├── QUICK_REFERENCE.md (Cheat sheet with commands)
│   ├── DEVELOPMENT.md (Complete setup & troubleshooting)
│   ├── HYBRID_SETUP_SUMMARY.md (Why this approach?)
│   └── SETUP_VALIDATION.md (Verification checklist)
│
├── 🏗️ Architecture Documents
│   ├── HANDSHAKE.md (API & data flow)
│   └── documentation/
│       └── architecture.md (System design)
│
├── 🐳 Docker & Infrastructure
│   ├── docker-compose.yml (PostgreSQL + RabbitMQ)
│   ├── dev-setup.sh (Automated setup - macOS/Linux)
│   └── dev-setup.bat (Automated setup - Windows)
│
├── ⚙️ Configuration
│   ├── .env (Local environment variables)
│   ├── .env.example (Template)
│   └── .gitignore (Git exclusions)
│
├── 🐍 Backend (Python - Run Locally)
│   ├── backend/
│   │   ├── requirements.txt (Core dependencies)
│   │   ├── requirements-dev.txt (Optional dev tools)
│   │   ├── Dockerfile (For production builds)
│   │   └── src/
│   │       ├── main.py (FastAPI service - Terminal 1)
│   │       ├── worker.py (RabbitMQ consumer - Terminal 2)
│   │       ├── models.py (Pydantic schemas)
│   │       └── analytics.py (Safety scoring logic)
│   │
│   ├── sql/
│   │   └── init.sql (Database initialization)
│   │
│   └── test_handshake.py (Integration test - Terminal 3)
│
├── 📋 Other Files
│   ├── ingestion-service/ (Placeholder for future)
│   └── .git/ (Version control)
```

---

## 📖 Reading Guide

### 🎯 First Time? Start Here

1. **START_HERE.md** (5 min)

   - Quick overview
   - How to get running
   - Where to find things

2. **QUICK_REFERENCE.md** (2 min)
   - Commands you'll use every day
   - Important URLs
   - Quick troubleshooting

### 🚀 Getting Started

3. **DEVELOPMENT.md** (20 min)

   - Complete setup instructions
   - How to run services locally
   - How to debug in VS Code
   - Detailed troubleshooting

4. **SETUP_VALIDATION.md** (10 min)
   - Verify each component works
   - Database checks
   - End-to-end test

### 🏗️ Understanding the Architecture

5. **HANDSHAKE.md** (15 min)

   - API endpoints & request/response format
   - Data flow diagram
   - Component descriptions

6. **architecture.md** (30 min)
   - Deep dive into system design
   - Database schema details
   - Why these technologies?

---

## 🎯 Use Cases

### "I want to get started quickly"

1. Read: **START_HERE.md**
2. Run: `docker-compose up -d`
3. Run: `python -m uvicorn src.main:app --reload`
4. Test: `python test_handshake.py`

### "I'm stuck on setup"

1. Check: **SETUP_VALIDATION.md**
2. Read: **DEVELOPMENT.md** → Troubleshooting section
3. Follow: Step-by-step checklist

### "I want to understand how it works"

1. Read: **HANDSHAKE.md** (API & flow)
2. Read: **HYBRID_SETUP_SUMMARY.md** (Why this approach)
3. Review: **architecture.md** (Deep dive)

### "I want to write code"

1. Open: **QUICK_REFERENCE.md** (Keep nearby)
2. Edit: Files in `backend/src/`
3. Watch: Terminal for auto-reload
4. Test: Via Swagger UI at http://localhost:8000/docs

### "Something's broken"

1. Check: **QUICK_REFERENCE.md** → Troubleshooting Cheat Sheet
2. Read: **DEVELOPMENT.md** → Troubleshooting section
3. Run: **SETUP_VALIDATION.md** to check each component

---

## 📊 File Types & Purposes

### Documentation 📚

| File                    | Purpose              | Read Time |
| ----------------------- | -------------------- | --------- |
| START_HERE.md           | Orientation guide    | 5 min     |
| README.md               | Project overview     | 5 min     |
| QUICK_REFERENCE.md      | Command cheat sheet  | 2 min     |
| DEVELOPMENT.md          | Complete setup guide | 20 min    |
| HYBRID_SETUP_SUMMARY.md | Why this approach    | 10 min    |
| SETUP_VALIDATION.md     | Verify setup         | 15 min    |
| HANDSHAKE.md            | API & data flow      | 15 min    |
| architecture.md         | System design        | 30 min    |

### Configuration ⚙️

| File               | Purpose                                |
| ------------------ | -------------------------------------- |
| .env               | Local environment variables            |
| .env.example       | Template for .env                      |
| docker-compose.yml | Infrastructure (PostgreSQL + RabbitMQ) |
| .gitignore         | Git exclusions                         |

### Scripts 🔧

| File          | Purpose                       | When       |
| ------------- | ----------------------------- | ---------- |
| dev-setup.sh  | Automated setup (macOS/Linux) | First time |
| dev-setup.bat | Automated setup (Windows)     | First time |

### Backend Code 🐍

| File              | Purpose           | Run        |
| ----------------- | ----------------- | ---------- |
| src/main.py       | FastAPI service   | Terminal 1 |
| src/worker.py     | RabbitMQ consumer | Terminal 2 |
| src/models.py     | Pydantic schemas  | (imported) |
| src/analytics.py  | Safety scoring    | (imported) |
| test_handshake.py | Integration test  | Terminal 3 |

### Database 🗄️

| File         | Purpose                                  |
| ------------ | ---------------------------------------- |
| sql/init.sql | Schema & tables (runs on docker startup) |

---

## 🔄 Typical Development Session

```
Start of Day:
├── docker-compose up -d (if not already running)
├── Terminal 1: python -m uvicorn src.main:app --reload
├── Terminal 2: python src/worker.py
└── Terminal 3: Ready for testing

During Development:
├── Edit src/main.py or src/worker.py
├── Save (Ctrl+S)
├── Watch Terminal 1 for "Reloading..."
├── Test via http://localhost:8000/docs
└── Repeat

End of Day:
└── Optional: docker-compose down
```

---

## 🗂️ Backend Structure

```
backend/
├── requirements.txt          # Core: FastAPI, Pydantic, psycopg, pika
├── requirements-dev.txt      # Optional: testing, debugging, linting
├── Dockerfile                # For production builds (not needed locally)
│
└── src/
    ├── main.py
    │   ├── FastAPI app setup
    │   ├── Database connection
    │   ├── RabbitMQ publisher
    │   ├── POST /api/v1/telemetry (Ingestion endpoint)
    │   └── GET /api/v1/trip/{trip_id}/score (Results endpoint)
    │
    ├── worker.py
    │   ├── RabbitMQ consumer
    │   ├── Database connection
    │   ├── Fetch telemetry blob
    │   ├── Call analytics.calculate_safety_score()
    │   └── Store results
    │
    ├── models.py
    │   ├── TelemetryPoint (single sensor reading)
    │   ├── TripPayload (API request)
    │   ├── TripIngestResponse (202 response)
    │   └── DriverScore (result schema)
    │
    └── analytics.py
        └── calculate_safety_score(telemetry_blob)
            ├── Count harsh braking events (< -0.4g)
            ├── Count rapid acceleration (> 0.4g)
            └── Return: safety_score, event counts
```

---

## 🎓 Learning Outcomes

After working with this project, you'll understand:

✅ **FastAPI** - Async Python web framework  
✅ **RabbitMQ** - Message queue for async processing  
✅ **PostgreSQL** - Relational database with JSONB  
✅ **Claim Check Pattern** - Handling large payloads  
✅ **Vertical Slice** - End-to-end feature implementation  
✅ **Hybrid Development** - Local code + Docker infrastructure  
✅ **Async/Await** - Python async patterns  
✅ **Test-Driven Development** - Integration testing

---

## 🚀 Next Level (Future Enhancements)

After mastering the current setup:

- [ ] Add **React Frontend** (view scores, fleet stats)
- [ ] Add **Unit Tests** (pytest)
- [ ] Add **CI/CD Pipeline** (GitHub Actions)
- [ ] Add **Kubernetes Deployment**
- [ ] Add **Monitoring** (Prometheus/Grafana)
- [ ] Add **Authentication** (JWT)
- [ ] Add **Database Migrations** (Alembic)
- [ ] Add **API Versioning** (v2 endpoints)

---

## 💡 Pro Tips

### Keep This Open

Pin **QUICK_REFERENCE.md** in your editor for quick lookup of commands.

### Watch the Logs

Keep Terminal 1 and 2 visible to see:

- When FastAPI reloads
- When Worker processes messages
- Any errors immediately

### Use Swagger

Test all endpoints at **http://localhost:8000/docs** instead of memorizing curl commands.

### Check RabbitMQ

Monitor queue at **http://localhost:15672** (guest/guest) to see messages piling up or getting processed.

---

## 🎉 You're Ready!

Everything is set up and documented.

**Next step:** Open **START_HERE.md** and follow the 5-minute setup!

🚀 Happy coding!
