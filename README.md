# Project Setup

## Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

## Frontend  
```bash
cd frontend
bun install
bun start
```

## Environment
Backend: Create `.env` with `MONGO_URL`, `DB_NAME`, `JWT_SECRET_KEY`  
Frontend: Uses `REACT_APP_API_URL` (defaults to http://localhost:8000)

## Test
```bash
python backend/test_api.py
```
