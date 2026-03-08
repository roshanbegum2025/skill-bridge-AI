/* ============================================================
   SkillBridge AI — script.js
   Handles: Resume Analysis, Internship Matching, Career Chat
   ============================================================ */

// ─── CONFIG ──────────────────────────────────────────────────
// 🔧 TODO: Replace with your actual API Gateway URL after deploying
// Example: "https://abc123.execute-api.us-east-1.amazonaws.com/prod"
const API_BASE_URL = "https://q4ffup9s4g.execute-api.ap-south-1.amazonaws.com";

// ─── DEMO MODE ───────────────────────────────────────────────
// Set to true to use mock responses (no backend needed for UI testing)
const DEMO_MODE = true;


/* ============================================================
   UTILITY HELPERS
   ============================================================ */

/**
 * Show or hide an element by toggling the "hidden" class
 */
function show(id) { document.getElementById(id)?.classList.remove("hidden"); }
function hide(id) { document.getElementById(id)?.classList.add("hidden"); }

/**
 * Make an API call to the Flask backend
 * Falls back to demo data if DEMO_MODE is true
 */
async function callAPI(endpoint, payload) {
  if (DEMO_MODE) {
    // Simulate network delay
    await sleep(1800);
    return getDemoData(endpoint, payload);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${response.status}`);
  }

  return response.json();
}

/** Simple sleep helper */
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/** Update character counter under resume textarea */
document.getElementById("resumeText").addEventListener("input", function () {
  document.getElementById("charCount").textContent = `${this.value.length} characters`;
});


/* ============================================================
   FEATURE 1 — RESUME ANALYZER
   ============================================================ */

async function analyzeResume() {
  const resumeText = document.getElementById("resumeText").value.trim();

  // Validate input
  if (!resumeText) {
    alert("Please paste your resume text first.");
    return;
  }
  if (resumeText.length < 50) {
    alert("Please provide more resume content (at least 50 characters).");
    return;
  }

  // UI: show loading, hide previous results
  hide("resumeEmpty");
  hide("resumeContent");
  show("resumeLoading");

  // Disable button during request
  const btn = document.getElementById("analyzeBtn");
  btn.disabled = true;
  btn.textContent = "Analyzing…";

  try {
    const data = await callAPI("/analyze_resume", { resume_text: resumeText });

    // Render results
    renderTags("techSkills", data.technical_skills || [], "tag-tech");
    renderTags("softSkills", data.soft_skills || [], "tag-soft");
    renderCareerPaths("careerPaths", data.career_paths || []);

    hide("resumeLoading");
    show("resumeContent");

  } catch (err) {
    hide("resumeLoading");
    show("resumeEmpty");
    alert(`Error analyzing resume: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">✦</span> Analyze Resume`;
  }
}

/** Renders skill tags inside a container */
function renderTags(containerId, items, cssClass) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!items.length) {
    container.innerHTML = `<span style="color:var(--text-3);font-size:13px">None detected</span>`;
    return;
  }

  items.forEach((item, i) => {
    const tag = document.createElement("span");
    tag.className = `tag ${cssClass}`;
    tag.textContent = item;
    tag.style.animationDelay = `${i * 40}ms`;
    container.appendChild(tag);
  });
}

/** Renders career path items */
function renderCareerPaths(containerId, paths) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!paths.length) {
    container.innerHTML = `<span style="color:var(--text-3);font-size:13px">No paths detected</span>`;
    return;
  }

  paths.forEach((path, i) => {
    const item = document.createElement("div");
    item.className = "career-item";
    item.textContent = path;
    item.style.animationDelay = `${i * 60}ms`;
    container.appendChild(item);
  });
}


/* ============================================================
   FEATURE 2 — INTERNSHIP COMPATIBILITY
   ============================================================ */

async function matchInternship() {
  const resumeText = document.getElementById("resumeText").value.trim();
  const role = document.getElementById("internshipRole").value;

  if (!resumeText) {
    alert("Please paste your resume in Section 1 first.");
    document.getElementById("resumeText").focus();
    return;
  }
  if (!role) {
    alert("Please select an internship role.");
    return;
  }

  // UI: show loading, hide previous score
  hide("scoreArea");
  show("matchLoading");

  const btn = document.getElementById("matchBtn");
  btn.disabled = true;

  try {
    const data = await callAPI("/match_internship", {
      resume_text: resumeText,
      internship_role: role,
    });

    renderScore(role, data.score, data.explanation);
    hide("matchLoading");
    show("scoreArea");

  } catch (err) {
    hide("matchLoading");
    alert(`Error calculating match: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span class="btn-icon">◈</span> Check Compatibility`;
  }
}

/**
 * Renders the compatibility score card with animated bar
 */
function renderScore(role, score, explanation) {
  const scoreNum = Math.max(0, Math.min(100, Math.round(score)));

  document.getElementById("scoreRole").textContent = role;
  document.getElementById("scoreNumber").textContent = scoreNum;
  document.getElementById("scoreExplanation").textContent = explanation;

  // Animate score number counting up
  let current = 0;
  const duration = 1200;
  const step = scoreNum / (duration / 16);
  const counter = setInterval(() => {
    current = Math.min(current + step, scoreNum);
    document.getElementById("scoreNumber").textContent = Math.round(current);
    if (current >= scoreNum) clearInterval(counter);
  }, 16);

  // Animate progress bar (small delay for visual effect)
  setTimeout(() => {
    document.getElementById("scoreBarFill").style.width = `${scoreNum}%`;
  }, 100);

  // Set tier label and colour
  const tierEl = document.getElementById("scoreTier");
  if (scoreNum >= 80) {
    tierEl.textContent = "Excellent Match";
    tierEl.className = "score-tier tier-excellent";
  } else if (scoreNum >= 60) {
    tierEl.textContent = "Good Match";
    tierEl.className = "score-tier tier-good";
  } else if (scoreNum >= 40) {
    tierEl.textContent = "Fair Match";
    tierEl.className = "score-tier tier-fair";
  } else {
    tierEl.textContent = "Low Match";
    tierEl.className = "score-tier tier-low";
  }
}


/* ============================================================
   FEATURE 3 — CAREER CHATBOT
   ============================================================ */

/** Holds the conversation history for context */
let chatHistory = [];

/** Send a message when Enter is pressed (Shift+Enter = new line) */
function handleChatKey(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChat();
  }
}

/** Use a suggested prompt chip */
function usePrompt(btn) {
  const input = document.getElementById("chatInput");
  input.value = btn.textContent;
  // Remove suggestion chips after first use
  document.getElementById("suggestedPrompts")?.remove();
  input.focus();
}

async function sendChat() {
  const input = document.getElementById("chatInput");
  const question = input.value.trim();

  if (!question) return;

  // Clear input and hide suggestion chips
  input.value = "";
  document.getElementById("suggestedPrompts")?.remove();

  // Append user message to UI
  appendMessage("user", question);

  // Add to history
  chatHistory.push({ role: "user", content: question });

  // Show typing indicator
  const typingId = showTyping();

  // Disable send button
  const btn = document.getElementById("sendBtn");
  btn.disabled = true;

  try {
    const data = await callAPI("/chat", { question, history: chatHistory });

    // Remove typing indicator, add AI response
    removeTyping(typingId);
    appendMessage("ai", data.response);

    // Add AI response to history
    chatHistory.push({ role: "assistant", content: data.response });

    // Keep history manageable (last 10 exchanges = 20 messages)
    if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);

  } catch (err) {
    removeTyping(typingId);
    appendMessage("ai", `Sorry, I encountered an error: ${err.message}. Please try again.`);
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

/** Adds a message bubble to the chat window */
function appendMessage(role, text) {
  const container = document.getElementById("chatMessages");

  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg msg-${role}`;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = role === "ai" ? "AI" : "You";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  // Render line breaks and simple formatting
  bubble.innerHTML = formatChatText(text);

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);
  container.appendChild(msgDiv);

  // Auto-scroll to bottom
  container.scrollTop = container.scrollHeight;
}

/** Basic text formatting: newlines → paragraphs, **bold** support */
function formatChatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")  // bold
    .split("\n\n")
    .map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
}

/** Shows a typing indicator and returns its DOM element ID */
function showTyping() {
  const id = `typing-${Date.now()}`;
  const container = document.getElementById("chatMessages");

  const msgDiv = document.createElement("div");
  msgDiv.className = "chat-msg msg-ai";
  msgDiv.id = id;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = "AI";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = `<div class="typing-indicator">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>`;

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;

  return id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}


/* ============================================================
   NAVIGATION — Smooth scroll + active link tracking
   ============================================================ */

document.querySelectorAll(".nav-link").forEach(link => {
  link.addEventListener("click", function () {
    document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
    this.classList.add("active");
  });
});

// Highlight nav link based on scroll position
window.addEventListener("scroll", () => {
  const sections = ["resume", "match", "chat"];
  let current = "resume";

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el && window.scrollY >= el.offsetTop - 120) current = id;
  });

  document.querySelectorAll(".nav-link").forEach(link => {
    link.classList.toggle("active", link.dataset.section === current);
  });
});


/* ============================================================
   DEMO DATA — Mock responses for UI testing without a backend
   ============================================================ */

function getDemoData(endpoint, payload) {
  switch (endpoint) {
    case "/analyze_resume":
      return {
        technical_skills: ["Python", "JavaScript", "React", "SQL", "Django", "REST APIs", "Git", "Docker", "Machine Learning"],
        soft_skills: ["Problem Solving", "Team Collaboration", "Communication", "Adaptability", "Leadership"],
        career_paths: [
          "Full-Stack Software Engineer",
          "Machine Learning Engineer",
          "Backend Developer (Python/Django)",
          "Data Analyst",
        ],
      };

    case "/match_internship":
      const role = payload.internship_role;
      const scores = {
        "AI Engineer Intern": { score: 82, explanation: "Your Python background and machine learning project experience are a strong foundation for an AI Engineer role. Your REST API experience and Django skills show you can integrate ML models into production systems. Consider strengthening your knowledge of PyTorch or TensorFlow to further boost your profile." },
        "Data Scientist Intern": { score: 75, explanation: "Your SQL knowledge and ML project experience align well with data science requirements. Your Python proficiency is a major asset. To improve your match score, consider adding experience with pandas, NumPy, and data visualization libraries like Matplotlib or Plotly." },
        "Web Developer Intern": { score: 91, explanation: "Excellent match! Your React, JavaScript, and Node.js skills are exactly what web developer internships require. Your full-stack project experience and REST API knowledge show you can contribute immediately. Strong portfolio evidence of past projects will seal the deal." },
      };
      return scores[role] || { score: 68, explanation: "Your technical foundation is solid and transfers well to this role. Focus on gaining specific domain experience through projects or online courses to stand out as a candidate." };

    case "/chat":
      const responses = [
        "Great question! For a career in tech, I'd recommend focusing on building a strong portfolio of real-world projects. Employers value practical experience over theoretical knowledge alone. Start with small projects and gradually tackle more complex ones that showcase problem-solving skills.\n\nAlso, contribute to open-source projects — this demonstrates collaboration skills and gives you real code to show in interviews.",
        "To prepare for technical interviews, focus on these key areas:\n\n**Data Structures & Algorithms** — Practice on LeetCode (aim for easy/medium)\n**System Design** — Learn about scalability, databases, APIs\n**Behavioral Questions** — Use the STAR method (Situation, Task, Action, Result)\n\nMost importantly, practice explaining your thought process out loud.",
        "Standing out as a candidate comes down to three things: a clean, results-focused resume, a strong GitHub portfolio with documented projects, and the ability to clearly communicate how your skills solve real problems.\n\nNetworking also matters — connect with professionals on LinkedIn and attend tech meetups or virtual events in your target field.",
      ];
      return { response: responses[Math.floor(Math.random() * responses.length)] };

    default:
      throw new Error("Unknown endpoint in demo mode");
  }
}
