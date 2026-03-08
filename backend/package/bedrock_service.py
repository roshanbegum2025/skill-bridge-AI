"""
SkillBridge AI — bedrock_service.py
Handles all Amazon Bedrock (Claude 3 Haiku) API calls.

This module contains:
  - analyze_resume_with_ai()  → Extract skills + career paths
  - match_internship_with_ai() → Score resume vs role
  - chat_with_ai()            → Career advice conversation
"""

import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# ─── Bedrock Configuration ────────────────────────────────────
# AWS region where Bedrock is enabled (must have Claude model access)
AWS_REGION = "us-east-1"

# Claude 3 Haiku model ID — fast and cost-effective
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Initialize the Bedrock client
# In Lambda, credentials come automatically from the execution role.
# Locally, ensure AWS CLI is configured: `aws configure`
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION,
)


def call_bedrock(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    """
    Low-level helper: sends a message to Claude via Amazon Bedrock.

    Args:
        system_prompt:  Instructions for how Claude should behave
        user_message:   The user's input / question
        max_tokens:     Maximum length of the AI response

    Returns:
        The AI's response as a plain string.

    Raises:
        RuntimeError if the Bedrock API call fails.
    """
    try:
        # Build the request body for the Claude Messages API
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message}
            ],
        }

        # Call Amazon Bedrock
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )

        # Parse the response
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error("Bedrock ClientError [%s]: %s", error_code, str(e))
        raise RuntimeError(f"Bedrock API error ({error_code}): {str(e)}")

    except Exception as e:
        logger.error("Bedrock call failed: %s", str(e))
        raise RuntimeError(f"Bedrock call failed: {str(e)}")


def parse_json_response(text: str) -> dict:
    """
    Safely parse a JSON response from Claude.
    Claude sometimes wraps JSON in markdown code blocks — this handles that.
    """
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        cleaned = "\n".join(lines[1:-1])

    return json.loads(cleaned)


# ─── Function 1: Resume Analyzer ─────────────────────────────
def analyze_resume_with_ai(resume_text: str) -> dict:
    """
    Sends resume text to Claude and extracts structured skill data.

    Returns:
        {
            "technical_skills": ["Python", "React", ...],
            "soft_skills": ["Communication", "Leadership", ...],
            "career_paths": ["Software Engineer", "Data Analyst", ...]
        }
    """
    system_prompt = """You are an expert career counselor and resume analyst.
Your job is to analyze resumes and extract structured information.
Always respond with valid JSON only — no extra text, no markdown fences.
Be thorough but concise. Focus on actionable, specific skills."""

    user_message = f"""Analyze the following resume and extract:
1. Technical skills (programming languages, tools, frameworks, technologies)
2. Soft skills (interpersonal, leadership, organizational abilities)
3. Suggested career paths (3-4 specific job titles that fit this profile)

Respond ONLY with this JSON structure (no other text):
{{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "career_paths": ["Career Path 1", "Career Path 2", "Career Path 3"]
}}

Resume:
{resume_text}"""

    try:
        raw_response = call_bedrock(system_prompt, user_message, max_tokens=800)
        result = parse_json_response(raw_response)

        # Ensure all expected keys exist with list values
        return {
            "technical_skills": result.get("technical_skills", []),
            "soft_skills":       result.get("soft_skills", []),
            "career_paths":      result.get("career_paths", []),
        }

    except json.JSONDecodeError:
        # If JSON parsing fails, return a graceful fallback
        logger.warning("Failed to parse JSON from Claude resume analysis")
        return {
            "technical_skills": ["Unable to parse — check resume format"],
            "soft_skills": [],
            "career_paths": [],
        }


# ─── Function 2: Internship Compatibility ────────────────────
# Internship descriptions used to give Claude context about each role
INTERNSHIP_DESCRIPTIONS = {
    "AI Engineer Intern": """
        Role: Build and deploy AI/ML models in production systems.
        Required: Python, machine learning frameworks (TensorFlow/PyTorch),
        experience with LLMs or NLP, REST APIs, cloud platforms (AWS/GCP).
        Nice-to-have: MLOps, Docker, data pipelines, prompt engineering.
    """,
    "Data Scientist Intern": """
        Role: Analyze large datasets to derive business insights and build predictive models.
        Required: Python or R, SQL, statistics, data visualization (matplotlib/seaborn),
        pandas, numpy, experience with Jupyter notebooks.
        Nice-to-have: Machine learning (scikit-learn), A/B testing, Tableau.
    """,
    "Web Developer Intern": """
        Role: Build and maintain web applications for end users.
        Required: HTML/CSS/JavaScript, React or Vue.js, Git version control,
        REST API integration, responsive design.
        Nice-to-have: Node.js, TypeScript, testing frameworks, CI/CD.
    """,
    "Product Manager Intern": """
        Role: Define product requirements and work cross-functionally with engineering/design.
        Required: Communication, analytical thinking, basic understanding of software development,
        experience with roadmap tools (Jira/Notion), user research skills.
        Nice-to-have: SQL for data analysis, Figma, A/B testing knowledge.
    """,
    "UX Designer Intern": """
        Role: Design user interfaces and experiences for digital products.
        Required: Figma or Sketch, wireframing, prototyping, user research methods,
        visual design principles, portfolio of design work.
        Nice-to-have: CSS basics, usability testing, accessibility standards.
    """,
}

def match_internship_with_ai(resume_text: str, internship_role: str) -> dict:
    """
    Scores the compatibility between a resume and an internship role.

    Returns:
        {
            "score": 75,
            "explanation": "Your Python skills and ML project experience..."
        }
    """
    # Get role description, fall back to generic if not found
    role_description = INTERNSHIP_DESCRIPTIONS.get(
        internship_role,
        f"A typical {internship_role} position requiring relevant technical and soft skills."
    )

    system_prompt = """You are an expert technical recruiter evaluating candidate fit.
Score candidates honestly and constructively.
Always respond with valid JSON only — no extra text, no markdown."""

    user_message = f"""Evaluate how well this candidate matches the internship role.

INTERNSHIP ROLE: {internship_role}
ROLE REQUIREMENTS:
{role_description}

CANDIDATE RESUME:
{resume_text}

Provide:
1. A compatibility score from 0 to 100 (be realistic, not overly generous)
2. A 2-3 sentence explanation covering: what matches well, what's missing, and one actionable tip

Respond ONLY with this JSON (no other text):
{{
    "score": 75,
    "explanation": "Your explanation here..."
}}"""

    try:
        raw_response = call_bedrock(system_prompt, user_message, max_tokens=400)
        result = parse_json_response(raw_response)

        score = result.get("score", 50)
        # Clamp score to valid range
        score = max(0, min(100, int(score)))

        return {
            "score": score,
            "explanation": result.get("explanation", "Analysis complete."),
        }

    except (json.JSONDecodeError, ValueError):
        return {
            "score": 50,
            "explanation": "Could not parse AI response. Please try again.",
        }


# ─── Function 3: Career Chatbot ──────────────────────────────
def chat_with_ai(question: str, history: list) -> dict:
    """
    Responds to career questions with helpful, personalized advice.

    Args:
        question: The user's current message
        history:  List of previous messages [{"role": "user/assistant", "content": "..."}]

    Returns:
        { "response": "AI's answer..." }
    """
    system_prompt = """You are a knowledgeable and encouraging AI career advisor specializing in tech internships and early-career development.

Your personality:
- Warm, professional, and direct
- Give specific, actionable advice (not vague platitudes)
- Use concrete examples when helpful
- Acknowledge the user's situation before giving advice
- Keep responses concise but complete (2-4 short paragraphs max)

Your expertise:
- Tech internship preparation (coding interviews, portfolios, resumes)
- Career paths in software engineering, data science, AI/ML, product management, UX
- Skill development and learning roadmaps
- Networking and job search strategies
- Interview preparation and negotiation

If asked something outside your expertise, be honest and redirect helpfully."""

    # Build messages array with conversation history for context
    messages = []

    # Include previous conversation (limit to last 8 exchanges = 16 messages)
    recent_history = history[-16:] if len(history) > 16 else history
    for msg in recent_history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add the new question
    messages.append({"role": "user", "content": question})

    try:
        # Use multi-turn conversation format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "system": system_prompt,
            "messages": messages,
        }

        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )

        response_body = json.loads(response["body"].read())
        ai_response = response_body["content"][0]["text"]

        return {"response": ai_response}

    except Exception as e:
        logger.error("Chat AI call failed: %s", str(e))
        raise RuntimeError(f"Chat failed: {str(e)}")
