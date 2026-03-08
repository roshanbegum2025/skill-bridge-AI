"""
SkillBridge AI — app.py
Flask backend for the internship recommendation platform.
Runs locally and on AWS Lambda via Mangum adapter.

Routes:
  POST /analyze_resume   → Extract skills + career paths from resume
  POST /match_internship → Score resume vs internship role
  POST /chat             → Career advice chatbot
"""

import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from bedrock_service import (
    analyze_resume_with_ai,
    match_internship_with_ai,
    chat_with_ai,
)

# ─── App Setup ────────────────────────────────────────────────
app = Flask(__name__)

# Allow requests from your S3 frontend URL (update in production)
CORS(app, origins=["*"])  # In production, replace * with your S3 URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Health Check ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint for AWS ALB / monitoring."""
    return jsonify({"status": "ok", "service": "SkillBridge AI"})


# ─── Route 1: Resume Analyzer ─────────────────────────────────
@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    """
    Accepts resume text and returns AI-extracted:
      - technical_skills (list)
      - soft_skills (list)
      - career_paths (list)

    Request body: { "resume_text": "..." }
    """
    body = request.get_json(silent=True) or {}
    resume_text = body.get("resume_text", "").strip()

    # Input validation
    if not resume_text:
        return jsonify({"error": "resume_text is required"}), 400
    if len(resume_text) < 50:
        return jsonify({"error": "resume_text is too short (min 50 characters)"}), 400
    if len(resume_text) > 10000:
        return jsonify({"error": "resume_text is too long (max 10,000 characters)"}), 400

    try:
        logger.info("Analyzing resume (%d chars)", len(resume_text))
        result = analyze_resume_with_ai(resume_text)
        return jsonify(result), 200

    except Exception as e:
        logger.error("Resume analysis failed: %s", str(e))
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500


# ─── Route 2: Internship Compatibility ────────────────────────
@app.route("/match_internship", methods=["POST"])
def match_internship():
    """
    Scores a resume against an internship role.

    Request body: {
      "resume_text": "...",
      "internship_role": "AI Engineer Intern"
    }

    Returns: { "score": 0-100, "explanation": "..." }
    """
    body = request.get_json(silent=True) or {}
    resume_text = body.get("resume_text", "").strip()
    internship_role = body.get("internship_role", "").strip()

    if not resume_text:
        return jsonify({"error": "resume_text is required"}), 400
    if not internship_role:
        return jsonify({"error": "internship_role is required"}), 400

    try:
        logger.info("Matching resume to: %s", internship_role)
        result = match_internship_with_ai(resume_text, internship_role)
        return jsonify(result), 200

    except Exception as e:
        logger.error("Internship matching failed: %s", str(e))
        return jsonify({"error": f"Matching failed: {str(e)}"}), 500


# ─── Route 3: Career Chatbot ───────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    """
    Conversational career advisor.

    Request body: {
      "question": "What skills do I need for data science?",
      "history": [                    ← optional conversation history
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }

    Returns: { "response": "..." }
    """
    body = request.get_json(silent=True) or {}
    question = body.get("question", "").strip()
    history = body.get("history", [])   # previous messages for context

    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) > 2000:
        return jsonify({"error": "question is too long (max 2,000 characters)"}), 400

    # Validate history format (list of {role, content})
    if not isinstance(history, list):
        history = []

    try:
        logger.info("Chat question: %s...", question[:60])
        result = chat_with_ai(question, history)
        return jsonify(result), 200

    except Exception as e:
        logger.error("Chat failed: %s", str(e))
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


# ─── AWS Lambda Handler ────────────────────────────────────────
# This allows the Flask app to run inside AWS Lambda via API Gateway.
# Install with: pip install mangum
try:
    from mangum import Mangum
    handler = Mangum(app)   # AWS Lambda entry point
    print("Mangum adapter loaded — ready for AWS Lambda")
except ImportError:
    # Mangum not installed — that's fine for local development
    print("Mangum not found — running in local Flask mode only")


# ─── Local Dev Entry Point ─────────────────────────────────────
if __name__ == "__main__":
    print("Starting SkillBridge AI backend on http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host="0.0.0.0", port=5000)
