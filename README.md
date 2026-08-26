# 🚀 LinkedIn Jobs Radar & AI Resume Matcher

An AI-powered real-time LinkedIn job postings aggregator, resume parser, and application assistant built with **FastAPI**, **Tailwind CSS**, and **BeautifulSoup**.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.110-009688.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.0-38bdf8.svg)

---

## ✨ Features

- 🔍 **Real-Time LinkedIn Job Scraper**: Live queries with concurrent multi-batch fetching across LinkedIn guest endpoints (30–40+ fresh listings per page).
- 🇮🇳 **Indian Tech Market Default & LeetCode Compensation**:
  - Automatically estimates packages in **`₹ LPA`** based on crowdsourced **LeetCode Discuss (`India Compensation`)** and **Levels.fyi** data.
  - Distinct badges for **`💰 Verified Pay`**, **`⚡ LeetCode Verified`**, and **`📊 Indian Market Est.`**.
- 🛡️ **Service-Based Company Blacklist Filter**:
  - 1-click toggle to exclude Indian IT service firms and staffing body shops (TCS, Infosys, Wipro, Cognizant, HCL, Tech Mahindra, LTIMindtree, Accenture, Capgemini, etc.) to prioritize **direct product companies and tech startups**.
- 📄 **AI Resume Parser & Skill Matcher**:
  - Upload PDF/TXT resume or paste bio text.
  - Automatically extracts 80+ technical skills, years of experience, candidate titles, and calculates a **Match Score (0–100%)** for each opening.
- ✍️ **1-Click AI Tailored Cover Letter Generator**:
  - Generates custom, professional cover letters combining your resume highlights with the target job's specific requirements.
- 📌 **Bookmarks & Application Manager**:
  - Save interesting roles locally and export to **CSV** or **JSON**.
- 🌓 **Dark & Light Mode**: Modern glassmorphism UI with Tailwind CSS and Lucide icons.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn, HTTPX (async requests), BeautifulSoup4, PyPDF
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Tailwind CSS, Lucide Icons
- **Storage & Caching**: In-Memory TTL Cache + Browser LocalStorage

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd linkedin-jobs-portal
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python run.py
```
*(Or `uvicorn app.main:app --reload --port 8000`)*

### 4. Open in browser
Navigate to **`http://127.0.0.1:8000`** in your browser.

---

## 📁 Project Structure

```text
linkedin-jobs-portal/
├── app/
│   ├── main.py                  # FastAPI endpoints & routing
│   ├── services/
│   │   ├── scraper.py           # LinkedIn async scraper engine
│   │   ├── salary_engine.py     # LeetCode & Indian market compensation model
│   │   ├── company_filter.py    # Service companies blacklist filter
│   │   ├── resume_parser.py     # PDF extraction, matching & cover letters
│   │   ├── cache.py             # In-memory TTL cache
│   │   └── mock_data.py         # Smart fallback dataset
│   └── static/
│       ├── index.html           # Main responsive UI
│       ├── styles.css           # Custom styles & animations
│       └── app.js               # Frontend application logic
├── run.py                       # Server launcher
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 📜 License
MIT License. Built for developers and job seekers.
