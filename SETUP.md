# NEXUS Development Setup Guide

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd NEXUS
chmod +x setup.sh
./setup.sh all
```

## 🛠️ Available Commands

```bash
./setup.sh [command]

# Commands:
- `redis`    - Check Redis status
- `backend`  - Check backend status  
- `frontend` - Setup frontend dependencies
- `deps`     - Install Python dependencies
- `all`      - Complete setup (deps + redis + backend)
- `stop`     - Stop all services
- `status`   - Show service status
```

## 📋 Prerequisites

- **Python 3.12+** installed
- **Node.js 18+** installed  
- **Redis** (will be installed by script)
- **Git** for cloning

## 🔧 Manual Setup Steps

### 1. Backend Setup
```bash
# Start Redis
./setup.sh redis

# Start backend (with real AI)
./setup.sh backend
```

### 2. Frontend Setup
```bash
# Install dependencies and start dev server
./setup.sh frontend
```

## 🐛 Troubleshooting

### Backend Issues
- **Port already in use**: `pkill -f uvicorn` before starting
- **Redis connection**: Ensure Redis is running on port 6379
- **Rate limits**: Check `/app/core/rate_limiter.py` for limits

### Frontend Issues  
- **Dependencies**: Run `npm install` in frontend directory
- **CORS errors**: Backend must be running before frontend requests

### Environment Variables
Create `.env` file with:
```
JOB_SEARCH_API=your_api_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key  
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
GROQ_API_KEY=your_groq_key  # Optional - for real AI
LLM_USE_MOCK=false  # Set to false for real AI
```

## 🌐 Development Workflow

1. **Backend**: `http://localhost:8000`
2. **Frontend**: `http://localhost:5174`  
3. **Redis**: `redis://localhost:6379`

## 📱 Features

- ✅ **Resume Upload & Parsing**
- ✅ **AI-Powered Resume Enhancement** (Real/Mock modes)
- ✅ **Professional CV Generation** 
- ✅ **Job Matching with Similarity Scores**
- ✅ **Rate Limiting** (Redis-based sliding window)
- ✅ **CORS Enabled**
- ✅ **Error Handling & Logging**

## 🔐 Security Notes

- All API endpoints require authentication
- Rate limiting enforced per user/route
- CORS configured for development
- Input validation on all endpoints

## 📞 Monitoring

Check logs with:
```bash
./setup.sh status
```

## 🚀 Production Deployment

For production, modify:
- Environment variables (use real API keys)
- Database connections
- Rate limits (adjust based on traffic)
- SSL certificates
- Domain configuration

---

## Backend startup

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

or

LLM_USE_MOCK=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

check if running:
curl http://127.0.0.1:8000/health