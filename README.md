# QuizMate AI — React + FastAPI Hackathon Demo

A polished AI quiz and study assistant prototype for a hackathon.

## Stack
- Frontend: React + TypeScript + Vite + React Router + Axios + Lucide React
- Backend: Python + FastAPI
- Database: SQLite
- PDF: PyMuPDF
- AI: configurable LLM API via environment variables
- Deployment: Vercel (frontend) + Render (backend)

## Features
- Register/login
- Preloaded popular topics
- Quiz configuration: 5/10/15/20 questions, question type, difficulty
- AI-generated MCQ / True-False / Short Answer
- PDF upload to generate questions
- PDF summarizer
- Score + explanations
- Quiz history / progress
- Weak-topic style feedback in results
- Demo mode if no AI key is configured

## Project structure

quizmate-ai/
  frontend/
  backend/
  data/topics/

## 1. Backend setup

Windows:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Mac/Linux:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend:
http://127.0.0.1:8000
Docs:
http://127.0.0.1:8000/docs

## 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend:
http://localhost:5173

Create `frontend/.env`:
```text
VITE_API_URL=http://127.0.0.1:8000
```

## 3. AI configuration

Backend `.env`:
```text
AI_API_KEY=your_key
AI_MODEL=your_model_name
JWT_SECRET=change-this-demo-secret
FRONTEND_ORIGIN=http://localhost:5173
```

If `AI_API_KEY` is empty, predefined demo questions are returned so the UI can still be demonstrated.

## 4. GitHub

At repository root:
```bash
git init
git add .
git commit -m "Initial QuizMate AI hackathon demo"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## 5. Deployment

### Backend on Render
Create a Web Service connected to the GitHub repository.

Root Directory:
```text
backend
```

Build:
```text
pip install -r requirements.txt
```

Start:
```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:
- AI_API_KEY
- AI_MODEL
- JWT_SECRET
- FRONTEND_ORIGIN=https://YOUR-VERCEL-DOMAIN.vercel.app

Render supports FastAPI Web Services and the Uvicorn start command shown above. See:
https://render.com/docs/deploy-fastapi

### Frontend on Vercel
Import the GitHub repository.

Root Directory:
```text
frontend
```

Build command:
```text
npm run build
```

Output:
```text
dist
```

Environment variable:
```text
VITE_API_URL=https://YOUR-RENDER-BACKEND.onrender.com
```

Vercel provides a Vite + React deployment template and supports zero-config Vite deployment.

## 6. Hackathon demo flow

1. Register/login.
2. Open Popular Topics.
3. Select Machine Learning.
4. Choose 10 or 20 questions.
5. Choose MCQ + Medium.
6. Generate quiz.
7. Answer and submit.
8. Show score, explanations and recommendation.
9. Upload a custom PDF.
10. Generate quiz from the PDF.
11. Open PDF Summarizer.
12. Show Progress / History.

## 7. Next advanced feature: RAG

For the final polish:
PDF -> chunking -> embeddings -> FAISS/Chroma -> retrieve relevant chunks -> LLM -> grounded quiz.

Do this only after the core demo works.
