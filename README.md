# 🚀 JobsRadar - LinkedIn Job Search, AI Matcher & Autonomous Auto-Applier

An intelligent, AI-powered LinkedIn job discovery platform, resume matching suite, and **autonomous 1-Click Auto-Applier** built with **FastAPI**, **Playwright**, **Tailwind CSS**, and **BeautifulSoup**.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.110-009688.svg)
![Playwright](https://img.shields.io/badge/Playwright-v1.40%2B-45ba4b.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.0-38bdf8.svg)

---

## ✨ Full Feature Overview

### 1. 🔍 Real-Time LinkedIn Job Scraper & Search
- **Live Concurrent Multi-Batch Queries**: Retrieves 30–40+ fresh listings per page via guest endpoints without requiring LinkedIn API keys or personal logins.
- **Default Indian Tech Hub Search**: Opens by default to live **Software Engineer** opportunities across **India** (*Bengaluru, Hyderabad, Pune, Delhi NCR, Mumbai, Remote*).
- **Multi-Factor Filters**: Filter by workplace (*Remote, Hybrid, On-site*), experience level (*Internship, Entry, Mid-Senior, Lead*), job type, and posted date (*Past 24h, Past Week, Past Month*).

### 2. 💰 LeetCode & Indian Tech Market Salary Intelligence
- **Default in `₹ LPA` (Lakhs Per Annum)**: Calibrated against Indian product company standards, startups, and MNC GCCs.
- **⚡ Crowdsourced LeetCode & Levels.fyi Compensation Tiers**:
  - **Tier-1 Tech Giants** (*Google, Microsoft, Amazon, Uber, Atlassian, Adobe, Salesforce, Oracle, Walmart*):
    - *SDE-1 (0–2 YOE)*: `₹22 LPA - ₹36 LPA`
    - *SDE-2 (2–5 YOE)*: `₹42 LPA - ₹70 LPA`
    - *Senior / Staff SDE (5–8+ YOE)*: `₹65 LPA - ₹1.1 Cr+`
  - **Top Indian Unicorns** (*Swiggy, Flipkart, Razorpay, Zomato, Zepto, Blinkit, PhonePe, Cred, Meesho*):
    - *SDE-1 (0–2 YOE)*: `₹18 LPA - ₹30 LPA`
    - *SDE-2 (2–5 YOE)*: `₹32 LPA - ₹55 LPA`
    - *Senior / Tech Lead (5–8 YOE)*: `₹45 LPA - ₹75 LPA`
- **3 Visual Compensation Badges**:
  - 🟢 **`💰 Verified Pay`**: Exact package scraped directly from employer description.
  - 🟣 **`⚡ LeetCode Verified`**: Crowdsourced community benchmark for top tech firms.
  - 🟡 **`📊 Indian Market Est.`**: Seniority & specialization formula.

### 3. 🛡️ IT Service Company Blacklist Filter
- **1-Click Toggle**: Enable **"Exclude IT Service Firms"** in the sidebar.
- **Comprehensive Blacklist**: Automatically hides mass-recruiting IT service firms & body-shopping staffing agencies (*TCS, Infosys, Wipro, Cognizant, HCLTech, Tech Mahindra, LTIMindtree, Capgemini, Accenture, Hexaware, Mphasis, Collabera, TeamLease, Quess, Randstad, TEKsystems, etc.*), leaving you with **direct product companies and high-growth tech startups**.

### 4. 🤖 Playwright 1-Click Auto-Applier with Interactive Screening Solver
- **Automated Form Filling**: Spawns a Chromium browser session that navigates to the job, clicks *Easy Apply*, fills contact info, and attaches your resume PDF.
- **❓ Interactive Missing Question Solver**:
  - Auto-answers standard questions from resume context (*e.g., "Years of experience in Python?"* -> `5 years`).
  - For unknown questions (*e.g., "Current CTC / notice period?"*), **pauses execution and pops up an interactive modal in the web UI** asking you once.
- **🧠 Persistent Memory (`candidate_profile.json`)**: Saves your answers so you **never have to answer the same question twice** across multiple applications!
- **🛡️ Human-in-the-Loop Review**: Stops at the final review screen so you can verify the details in the visible browser window before submitting.
- **⚙️ Candidate Auto-Apply Profile**: Configure your phone, notice period, CTC, and work authorization preferences from the top navbar.

### 5. 📄 AI Resume Parser & Match Scoring
- **PDF & Text Ingestion**: Upload your resume PDF or paste raw bio text.
- **Deep Skill Extraction**: Identifies 80+ modern technologies (*Python, React, FastAPI, Docker, Kubernetes, AWS, SQL, PyTorch, etc.*).
- **0–100% Match Scoring**: Calculates real-time compatibility scores for every job card with color-coded badges and checklist highlights (`✓ Python`).

### 6. ✍️ 1-Click AI Tailored Cover Letter Generator
- Click **"Cover Letter"** on any job details card to generate a custom, professional cover letter combining your specific resume projects/skills with the target company's job requirements.
- 1-Click copy to clipboard.

### 7. 📌 Bookmarks, Saved Jobs & Data Export
- **Persistent Bookmarks**: Save interesting job openings locally in browser storage.
- **Data Export**: Export search results or saved jobs to **CSV** or **JSON**.

### 8. 🌓 Modern Responsive UI / UX
- **Glassmorphism Design**: Built with Tailwind CSS and Lucide icons.
- **Dark & Light Mode**: Seamless theme switcher with persistent local storage preferences.

---

## 🛠️ Architecture & Tech Stack

```text
linkedin-jobs-portal/
├── app/
│   ├── main.py                  # FastAPI REST endpoints & routing
│   ├── services/
│   │   ├── auto_applier.py      # Playwright browser automation agent
│   │   ├── profile_store.py     # Candidate memory & Q&A store
│   │   ├── scraper.py           # Multi-batch async LinkedIn scraper
│   │   ├── salary_engine.py     # LeetCode & Indian market compensation model
│   │   ├── company_filter.py    # IT Service companies blacklist filter
│   │   ├── resume_parser.py     # PDF extraction, matching & cover letters
│   │   ├── cache.py             # In-memory TTL cache
│   │   └── mock_data.py         # Fallback dataset
│   └── static/
│       ├── index.html           # Main responsive web UI & modals
│       ├── styles.css           # Custom styles & animations
│       └── app.js               # Frontend application logic & state
├── candidate_profile.json       # Persistent candidate auto-fill memory
├── run.py                       # Server launcher
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/ankitsingh1708/Job-automation.git
cd Job-automation
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Run the application
```bash
python run.py
```
*(Or `uvicorn app.main:app --reload --port 8000`)*

### 4. Open in browser
Navigate to **`http://127.0.0.1:8000`** in your browser.

---

## 💡 How to Use Auto-Apply

1. **Set Up Profile**: Click **"Auto-Apply Profile"** in the top navbar to configure your standard notice period, CTC, and work authorization preferences.
2. **Upload Resume**: Click **"Upload Resume"** to upload your resume PDF.
3. **Search & Match**: Browse matching product company jobs with verified LeetCode compensation tags.
4. **Auto-Apply**: Click **"⚡ Auto-Apply with AI"** on any job card:
   - A live Chromium browser will open.
   - The bot auto-fills contact info and attaches your resume.
   - If a custom question is asked, answer it in the web UI modal (it will be remembered for future applications).
   - Review and submit!

---

## 📜 License
MIT License. Built for developers and job seekers.
