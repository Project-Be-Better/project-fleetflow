# 📚 FleetFlow Documentation Index

Welcome to the FleetFlow documentation! This folder contains all guides and references for the project.

---

## 🚀 Getting Started (Start Here!)

### New to the Project?

1. **[START_HERE.md](START_HERE.md)** - Quick 5-minute orientation guide
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Commands and URLs you'll use daily
3. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Complete setup and troubleshooting guide

### Setup Issues?

- **[SETUP_VALIDATION.md](SETUP_VALIDATION.md)** - Step-by-step verification checklist
- **[DEVELOPMENT.md](DEVELOPMENT.md#-troubleshooting)** - Detailed troubleshooting section

---

## 🏗️ Understanding the Architecture

### Want to Know How It Works?

1. **[HANDSHAKE.md](HANDSHAKE.md)** - API endpoints and vertical slice flow
2. **[architecture.md](architecture.md)** - System design and database schema
3. **[HYBRID_SETUP_SUMMARY.md](HYBRID_SETUP_SUMMARY.md)** - Why this development approach?

### Reference Materials

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File organization and navigation

---

## 📖 Documentation by Use Case

### "I want to get started quickly"

→ [START_HERE.md](START_HERE.md) (5 min)

### "I need to set up the development environment"

→ [DEVELOPMENT.md](DEVELOPMENT.md) (20 min)

### "I need a quick command reference"

→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (2 min)

### "Something's broken and I need to fix it"

→ [SETUP_VALIDATION.md](SETUP_VALIDATION.md) (15 min)
→ [DEVELOPMENT.md](DEVELOPMENT.md#-troubleshooting) (10 min)

### "I want to understand the architecture"

→ [HANDSHAKE.md](HANDSHAKE.md) (15 min)
→ [architecture.md](architecture.md) (30 min)

### "I'm new to the codebase"

→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) (5 min)

### "I want to know why this hybrid approach?"

→ [HYBRID_SETUP_SUMMARY.md](HYBRID_SETUP_SUMMARY.md) (10 min)

---

## 📋 All Documentation Files

| File                        | Purpose                          | Read Time | Best For            |
| --------------------------- | -------------------------------- | --------- | ------------------- |
| **START_HERE.md**           | Quick orientation & overview     | 5 min     | First-time setup    |
| **QUICK_REFERENCE.md**      | Command cheat sheet              | 2 min     | Daily development   |
| **DEVELOPMENT.md**          | Complete setup & troubleshooting | 20 min    | Full setup guide    |
| **SETUP_VALIDATION.md**     | Verification checklist           | 15 min    | After setup         |
| **SETUP_COMPLETE.md**       | Completion summary               | 10 min    | Overview            |
| **HANDSHAKE.md**            | API & data flow                  | 15 min    | Understanding flow  |
| **architecture.md**         | System design                    | 30 min    | Deep dive           |
| **HYBRID_SETUP_SUMMARY.md** | Why hybrid approach              | 10 min    | Understanding setup |
| **PROJECT_STRUCTURE.md**    | File organization                | 5 min     | Navigation          |

---

## 🎯 Quick Navigation

### Infrastructure & Setup

- 🐳 Docker: `docker-compose up -d`
- 📦 Requirements: `backend/requirements.txt`
- 🗄️ Database: `sql/init.sql`

### API Endpoints

- Base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health Check: `GET /health`
- Submit Telemetry: `POST /api/v1/telemetry`
- Get Score: `GET /api/v1/trip/{trip_id}/score`

### Development Services

- **FastAPI**: `python -m uvicorn src.main:app --reload`
- **Worker**: `python src/worker.py`
- **Test**: `python test_handshake.py`

### Monitoring

- RabbitMQ UI: `http://localhost:15672`
- Database: `psql postgresql://postgres:password@localhost:5432/fleetflow`

---

## 🎓 Learning Path

**Day 1 - Get Running:**

1. Read: [START_HERE.md](START_HERE.md)
2. Run: `docker-compose up -d`
3. Run: FastAPI + Worker
4. Test: `python test_handshake.py`

**Day 2 - Understand & Debug:**

1. Read: [DEVELOPMENT.md](DEVELOPMENT.md)
2. Explore: Swagger UI
3. Make changes and watch reload
4. Use: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Day 3 - Deep Dive:**

1. Read: [HANDSHAKE.md](HANDSHAKE.md)
2. Read: [architecture.md](architecture.md)
3. Review: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**Day 4+ - Build & Iterate:**

1. Use: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
2. Edit: Code in `backend/src/`
3. Watch: Auto-reload in Terminal 1
4. Test: Via Swagger UI

---

## 🔗 Important Links

**Project Files:**

- Backend: [`backend/`](../backend/)
- Database: [`sql/`](../sql/)
- Architecture: [`architecture/`](architecture/)

**Configuration:**

- Environment: [`.env`](../.env)
- Docker: [`docker-compose.yml`](../docker-compose.yml)
- Git: [`.gitignore`](../.gitignore)

---

## 💡 Pro Tips

### Bookmark These

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Daily commands
- [DEVELOPMENT.md](DEVELOPMENT.md#-troubleshooting) - Troubleshooting
- [HANDSHAKE.md](HANDSHAKE.md#-data-flow-specification) - API reference

### Keep These Open

- Terminal 1: FastAPI (watch for reload messages)
- Terminal 2: Worker (watch for message processing)
- Browser Tab: http://localhost:8000/docs (Swagger UI for testing)

### Common Commands

```bash
# Start everything
docker-compose up -d
python -m uvicorn src.main:app --reload

# Check status
docker-compose ps
curl http://localhost:8000/health

# Run tests
python test_handshake.py

# Database access
psql postgresql://postgres:password@localhost:5432/fleetflow
```

---

## 🆘 Need Help?

| Question               | Answer                                           |
| ---------------------- | ------------------------------------------------ |
| Where do I start?      | Read [START_HERE.md](START_HERE.md)              |
| How do I set up?       | Follow [DEVELOPMENT.md](DEVELOPMENT.md)          |
| What command was that? | Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)   |
| Something's broken     | See [SETUP_VALIDATION.md](SETUP_VALIDATION.md)   |
| How does it work?      | Read [HANDSHAKE.md](HANDSHAKE.md)                |
| Where's the code?      | See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |

---

## 📞 Documentation Sections

### START_HERE.md

- Quick overview
- 5-minute setup
- Key benefits

### QUICK_REFERENCE.md

- One-time setup
- Daily commands
- Important URLs
- Troubleshooting cheat sheet

### DEVELOPMENT.md

- Prerequisites
- Step-by-step setup
- Service running
- Testing & validation
- Monitoring
- Debugging
- Troubleshooting (detailed)

### SETUP_VALIDATION.md

- Infrastructure checks
- Python environment
- FastAPI verification
- Worker verification
- End-to-end test
- Hot-reload test
- Database verification
- RabbitMQ verification

### HANDSHAKE.md

- Executive summary
- Components & technologies
- Data flow (Phase A & B)
- Database schema
- API interface
- Development roadmap

### architecture.md

- System design
- Component overview
- Data specifications
- Architectural patterns

### HYBRID_SETUP_SUMMARY.md

- What changed
- Why this approach
- Infrastructure setup
- Python environment
- Service running
- Workflow details
- Troubleshooting

### PROJECT_STRUCTURE.md

- File organization
- Reading guide
- Backend structure
- Learning outcomes
- Pro tips

---

## 🎉 Ready to Start?

1. Open [START_HERE.md](START_HERE.md)
2. Follow the 5-minute quick start
3. Bookmark [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. Happy coding! 🚀

---

_Last updated: December 30, 2025_
