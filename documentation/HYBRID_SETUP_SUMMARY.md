# Hybrid Development Setup - Summary

## ✅ What Changed

You now have a **hybrid development environment** optimized for rapid iteration:

### Before ❌

- Everything ran in Docker containers
- Every code change required rebuilding Docker image
- Debugging difficult across containerized services
- Slow feedback loop (minutes per iteration)

### After ✅

- **Infrastructure in Docker**: PostgreSQL + RabbitMQ
- **Code runs locally**: FastAPI, Worker, Frontend (future)
- **Instant reload**: Changes apply immediately on save
- **Easy debugging**: Attach VS Code debugger directly
- **Fast feedback**: Seconds per iteration

---

## 📦 What You Get

### 1. Updated Docker Compose

- **Removed:** api and worker services from Docker
- **Kept:** PostgreSQL + RabbitMQ infrastructure
- **Lightweight:** Only essential services in containers

**File:** `docker-compose.yml`

```bash
docker-compose up -d  # Start infrastructure
```

### 2. Development Guide

Complete step-by-step setup with troubleshooting

**File:** `DEVELOPMENT.md`

- Local environment setup
- Running FastAPI with reload
- Running Worker
- Manual testing with curl
- Debugging in VS Code
- Common issues & solutions

### 3. Automated Setup Scripts

One-command setup for your platform

**Files:**

- `dev-setup.sh` (macOS/Linux) - `./dev-setup.sh`
- `dev-setup.bat` (Windows) - `dev-setup.bat`

### 4. Environment Configuration

Local `.env` file with sensible defaults

**File:** `.env`

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/fleetflow
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### 5. Development Dependencies

Optional dev tools for testing, debugging, linting

**File:** `backend/requirements-dev.txt`

```bash
pip install -r backend/requirements-dev.txt  # Optional
```

### 6. Updated README

Quick-start guide focusing on local development

**File:** `README.md`

---

## 🚀 Getting Started (3 Steps)

### 1. Start Infrastructure

```bash
docker-compose up -d
```

### 2. Run Services Locally

**Terminal 1 - FastAPI with auto-reload:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

**Terminal 2 - Worker:**

```bash
cd backend
source venv/bin/activate
python src/worker.py
```

### 3. Test End-to-End

**Terminal 3 - Handshake test:**

```bash
pip install aiohttp
python test_handshake.py
```

---

## ⚡ Development Workflow

### Edit Code → Instant Feedback

1. **Edit** `backend/src/main.py` or `backend/src/worker.py`
2. **Save** (Ctrl+S)
3. **FastAPI reloads automatically** ← Watch terminal for "Reloading..."
4. **Test via** Swagger UI or curl
5. **Worker picks up changes** immediately

No Docker rebuild needed! 🎉

---

## 🐛 Debugging in VS Code

Stop FastAPI and run with debugger:

```bash
python -m debugpy --listen 5678 -m uvicorn src.main:app
```

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Attach to FastAPI",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "127.0.0.1"
    }
  ]
}
```

Press **F5** to attach and debug! 🎯

---

## 📊 Port Reference

| Service     | Port  | URL                        | Purpose        |
| ----------- | ----- | -------------------------- | -------------- |
| FastAPI     | 8000  | http://localhost:8000      | API server     |
| Swagger     | 8000  | http://localhost:8000/docs | Test endpoints |
| PostgreSQL  | 5432  | localhost:5432             | Database       |
| RabbitMQ    | 5672  | localhost:5672             | Message queue  |
| RabbitMQ UI | 15672 | http://localhost:15672     | Queue monitor  |

---

## 📚 Documentation Map

| File                          | Purpose            | Read When       |
| ----------------------------- | ------------------ | --------------- |
| README.md                     | Project overview   | First time      |
| **DEVELOPMENT.md**            | Complete dev guide | **Start here!** |
| HANDSHAKE.md                  | Architecture & API | Want details    |
| documentation/architecture.md | System design      | Deep dive       |

---

## 🎯 Key Benefits

### For You (Developer)

✅ **Instant Feedback** - No Docker rebuild, just Ctrl+S  
✅ **Easy Debugging** - Attach IDE debugger to running process  
✅ **Fast Iteration** - Seconds per change, not minutes  
✅ **Simplified Testing** - Test locally before containerizing  
✅ **Knowledge Transfer** - Clear separation of local vs Docker code

### For Your Team

✅ **Reproducible** - `.env` and `docker-compose.yml` ensure consistency  
✅ **Documented** - Setup scripts and guides reduce onboarding time  
✅ **Scalable** - Easy to add frontend, more workers, etc.  
✅ **Production-Ready** - Docker-based infrastructure mirrors production

---

## 🚦 Common Commands

### Start Everything

```bash
# Terminal 1 - Infrastructure
docker-compose up -d

# Terminal 2 - FastAPI (auto-reload)
cd backend && python -m uvicorn src.main:app --reload

# Terminal 3 - Worker
cd backend && python src/worker.py

# Terminal 4 - Test
python test_handshake.py
```

### Stop Everything

```bash
# Local services: Ctrl+C in terminals
# Infrastructure: docker-compose down
```

### Check Status

```bash
docker-compose ps          # Infrastructure status
docker logs fleetflow-db   # Database logs
docker logs fleetflow-mq   # RabbitMQ logs
```

### Troubleshoot

```bash
# Verify database is running
psql postgresql://postgres:password@localhost:5432/fleetflow -c "\dt telemetry.*"

# Check RabbitMQ queue
curl -u guest:guest http://localhost:15672/api/queues
```

---

## 📝 Next Steps

1. ✅ Read [DEVELOPMENT.md](DEVELOPMENT.md)
2. ✅ Run setup script (`dev-setup.sh` or `dev-setup.bat`)
3. ✅ Start services in three terminals
4. ✅ Run `python test_handshake.py`
5. ✅ Make a code change and watch it reload!
6. 📝 Start building features

---

## 💡 Tips & Tricks

### Watch File Changes

```bash
# Verify FastAPI is reloading
# Look for: "Uvicorn running on http://0.0.0.0:8000"
# And: "Application startup complete"
```

### Quick Test from CLI

```bash
# Submit telemetry
trip_id=$(curl -s -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"550e8400-e29b-41d4-a716-446655440000",...}' | jq -r '.trip_id')

# Wait 1 second
sleep 1

# Get score
curl http://localhost:8000/api/v1/trip/$trip_id/score
```

### Monitor RabbitMQ

```bash
# Open browser to management UI
open http://localhost:15672
# Username: guest
# Password: guest
```

### Database Queries

```bash
psql postgresql://postgres:password@localhost:5432/fleetflow

# List all trips
SELECT id, vehicle_id, status FROM telemetry.trip_logs;

# Get recent scores
SELECT trip_id, safety_score FROM telemetry.driver_scores ORDER BY created_at DESC LIMIT 5;
```

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic**: https://docs.pydantic.dev
- **RabbitMQ**: https://www.rabbitmq.com/documentation.html
- **PostgreSQL**: https://www.postgresql.org/docs

Enjoy rapid development! 🚀
