# SkillBridge AI 🌉

An AI-powered internship recommendation platform that bridges the gap between student skills and opportunities — built on AWS.

🔗 *Live Demo:* http://skillbridge-ai-frontend-afreens.s3-website.ap-south-1.amazonaws.com

---

## 📌 What It Does

SkillBridge AI helps students find the right internships by analyzing their resume, scoring compatibility with roles, and providing personalized career advice — all powered by Claude AI on Amazon Bedrock.

---

## ✨ Features

- *Resume Analyzer* — Paste or upload your resume → AI extracts technical skills, soft skills, and career paths
- *Internship Matcher* — Select a role → get a 0–100 compatibility score with explanation
- *AI Career Advisor* — Chat with an AI for interview tips, skill roadmaps, and career guidance

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask, Mangum |
| AI Model | Amazon Bedrock — Claude 3 Haiku |
| Serverless | AWS Lambda |
| API | Amazon API Gateway |
| Hosting | Amazon S3 (static website) |
| File Parsing | Amazon Textract (PDF upload) |

---

## 📁 Project Structure

skillbridge-ai/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── bedrock_service.py
│   └── requirements.txt
└── README.md


---

## 🔄 How It Works

User (Browser)
     │
     ▼
Amazon S3 — serves the frontend
     │
     ▼
API Gateway — receives POST requests
     │
     ▼
AWS Lambda — runs Flask backend
     │
     ▼
Amazon Bedrock — Claude 3 Haiku generates response
     │
     ▼
Response displayed in UI


---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /analyze_resume | Extract skills from resume text |
| POST | /analyze_resume_file | Upload PDF → extract + analyze |
| POST | /match_internship | Score resume vs role |
| POST | /chat | Career advisor chatbot |
| GET | /health | Health check |

---

## 💰 Cost Estimate

| Service | Est. Monthly Cost |
|---|---|
| Amazon Bedrock | ~$0.50–$2.00 |
| AWS Lambda | ~$0.00–$0.20 |
| API Gateway | ~$0.10–$1.00 |
| Amazon S3 | ~$0.01–$0.05 |
| *Total* | *~$1–$3/month* |

---

## 👩‍💻 Built By

*Logic Loops* — AWS AI for Bharat Hackathon 2025

Built with ❤️ using Flask · Amazon Bedrock · AWS Lambda · S3
