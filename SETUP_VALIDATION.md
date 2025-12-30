# Setup Validation Checklist

Use this checklist to verify your hybrid development environment is working correctly.

## ✅ Pre-Flight Check

- [ ] Docker Desktop is installed and running
- [ ] Python 3.11+ is installed
- [ ] Git is installed
- [ ] You have ~2GB free disk space for Docker images

---

## ✅ Infrastructure Setup

```bash
# Start infrastructure
docker-compose up -d

# Verify services are healthy
docker-compose ps
```

**Expected output:**

```
CONTAINER ID   NAMES              STATUS
abc123...      fleetflow-db       Up (healthy)
def456...      fleetflow-mq       Up (healthy)
```

Checklist:

- [ ] Both services show "Up (healthy)"
- [ ] No "exited" or "unhealthy" statuses

### Verify Services

**PostgreSQL:**

```bash
psql postgresql://postgres:password@localhost:5432/fleetflow -c "SELECT version();"
```

- [ ] Command succeeds and shows PostgreSQL version

**RabbitMQ:**

```bash
curl -u guest:guest http://localhost:15672/api/aliveness-test/%2F
```

- [ ] Returns status OK

---

## ✅ Python Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Checklist:

- [ ] Venv created without errors
- [ ] Venv activated (prompt shows `(venv)` prefix)
- [ ] pip install completes without errors
- [ ] Run `pip list | grep fastapi` - should show FastAPI

---

## ✅ FastAPI Service

**Terminal 1:**

```bash
cd backend
source venv/bin/activate
python -m uvicorn src.main:app --reload
```

**Expected output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
...
Application startup complete
```

Checklist:

- [ ] Service starts without errors
- [ ] Shows "Application startup complete"
- [ ] No error messages about database connection

**Verify in Browser/curl:**

```bash
curl http://localhost:8000/health
```

- [ ] Returns: `{"status":"healthy"}`
- [ ] Swagger UI works at http://localhost:8000/docs

---

## ✅ Worker Service

**Terminal 2:**

```bash
cd backend
source venv/bin/activate
python src/worker.py
```

**Expected output:**

```
🚀 Worker listening on queue: telemetry_analysis
Press CTRL+C to stop
```

Checklist:

- [ ] Worker starts without errors
- [ ] Shows "Worker listening on queue"
- [ ] No error messages about database connection

---

## ✅ End-to-End Handshake Test

**Terminal 3:**

```bash
pip install aiohttp
python test_handshake.py
```

**Expected output:**

```
============================================================
🚗 FleetFlow Vertical Slice Handshake Test
============================================================

1️⃣  Submitting telemetry...
✅ Accepted: trip_id = a1b2c3d4-...

2️⃣  Waiting for worker to process (max 10s)...

3️⃣  Retrieving calculated score...
✅ Score retrieved (attempt 1):
   Safety Score: 90/100
   Harsh Braking Events: 1
   Rapid Acceleration Events: 1

============================================================
✅ HANDSHAKE SUCCESSFUL!
============================================================
```

Checklist:

- [ ] Test completes successfully
- [ ] Trip is accepted with 202 status
- [ ] Score is retrieved within 10 seconds
- [ ] Final message shows "HANDSHAKE SUCCESSFUL"

---

## ✅ Code Hot-Reload Test

1. **Edit** `backend/src/main.py` - Add a comment or minor change
2. **Save** (Ctrl+S)
3. **Watch** Terminal 1 for "Reloading..." message
4. **Verify** the change took effect

Checklist:

- [ ] Changes are detected immediately
- [ ] Reloading message appears
- [ ] No errors during reload
- [ ] Service continues running

---

## ✅ Database Verification

```bash
psql postgresql://postgres:password@localhost:5432/fleetflow
```

Inside psql:

```sql
\dt telemetry.*
SELECT COUNT(*) FROM telemetry.trip_logs;
SELECT COUNT(*) FROM telemetry.driver_scores;
\q
```

Checklist:

- [ ] Both tables exist
- [ ] Tables have records from test
- [ ] Query executes without errors

---

## ✅ RabbitMQ Verification

Open http://localhost:15672 in browser

- Username: `guest`
- Password: `guest`

Checklist:

- [ ] Can log in successfully
- [ ] Queue `telemetry_analysis` appears in "Queues"
- [ ] Can see queue statistics

---

## 🎉 Complete Checklist

All items checked?

```
✅ Infrastructure (Docker)
✅ Python Environment
✅ FastAPI Service
✅ Worker Service
✅ End-to-End Handshake
✅ Hot Reload
✅ Database
✅ RabbitMQ UI
```

**Congratulations!** Your hybrid development environment is fully set up! 🚀

---

## 🚨 If Something Failed

1. **Check logs:**

   ```bash
   docker logs fleetflow-db
   docker logs fleetflow-mq
   ```

2. **Review DEVELOPMENT.md**

   - Section: "Troubleshooting"

3. **Common Fixes:**

   - Port already in use → `docker-compose down -v && docker-compose up -d`
   - Database not ready → Wait 10s and try again
   - Venv not activated → Run `source venv/bin/activate`

4. **Still stuck?**
   - Check file names match exactly (case-sensitive on macOS/Linux)
   - Verify Python version: `python --version` (should be 3.11+)
   - Check internet connection for pip install

---

## 📝 Next Steps

After validation passes:

1. Open `QUICK_REFERENCE.md` for common commands
2. Read `DEVELOPMENT.md` for detailed workflow
3. Review `HANDSHAKE.md` for architecture details
4. Start building features!

Happy coding! 🚀
