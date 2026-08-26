import os
import json
from typing import Dict, Any, Optional

PROFILE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "candidate_profile.json")

DEFAULT_PROFILE = {
    "full_name": "Ankur Singh",
    "email": "ankur.singh@example.com",
    "phone": "+91 9876543210",
    "city": "Bengaluru, Karnataka, India",
    "linkedin_url": "https://www.linkedin.com/in/ankit-singh",
    "github_url": "https://github.com/ankitsingh1708",
    "portfolio_url": "",
    "notice_period": "30 days",
    "current_ctc": "16 LPA",
    "expected_ctc": "28 LPA",
    "work_authorization": "Yes",
    "require_sponsorship": "No",
    "gender": "Decline to specify",
    "custom_answers": {
        "are you comfortable working hybrid / on-site": "Yes",
        "do you have a valid passport": "Yes",
        "willing to relocate": "Yes"
    }
}

def load_profile() -> Dict[str, Any]:
    """
    Loads candidate profile and screening memory from local JSON file.
    """
    if os.path.exists(PROFILE_FILE_PATH):
        try:
            with open(PROFILE_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults
                merged = dict(DEFAULT_PROFILE)
                merged.update(data)
                if "custom_answers" not in merged:
                    merged["custom_answers"] = {}
                return merged
        except Exception:
            return dict(DEFAULT_PROFILE)
    return dict(DEFAULT_PROFILE)

def save_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persists candidate profile and screening answers.
    """
    current = load_profile()
    current.update(profile_data)
    with open(PROFILE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    return current

def record_question_answer(question_text: str, answer_text: str) -> None:
    """
    Stores an answer to a custom recruiter screening question for future automatic re-use.
    """
    if not question_text or not answer_text:
        return
    norm_q = question_text.strip().lower()
    profile = load_profile()
    if "custom_answers" not in profile:
        profile["custom_answers"] = {}
    profile["custom_answers"][norm_q] = str(answer_text).strip()
    save_profile(profile)

def lookup_known_answer(question_text: str, resume_skills: list = None, experience_years: int = 4) -> Optional[str]:
    """
    Attempts to intelligently answer a recruiter screening question:
    1. Known profile values (Notice Period, CTC, Sponsorship, Phone)
    2. Technology experience questions ("How many years of Python?")
    3. Learned past answers in custom_answers
    """
    q = question_text.strip().lower()
    profile = load_profile()
    custom = profile.get("custom_answers", {})

    # 1. Exact or Fuzzy Custom Answers Memory
    if q in custom:
        return custom[q]
    for stored_q, stored_ans in custom.items():
        if stored_q in q or q in stored_q:
            return stored_ans

    # 2. Standard Common Screening Questions
    if any(k in q for k in ["notice period", "how soon can you join", "joining time"]):
        return profile.get("notice_period", "30 days")

    if any(k in q for k in ["current ctc", "current salary", "present ctc", "current compensation"]):
        return profile.get("current_ctc", "16 LPA")

    if any(k in q for k in ["expected ctc", "expected salary", "target salary", "salary expectation"]):
        return profile.get("expected_ctc", "28 LPA")

    if any(k in q for k in ["legally authorized", "authorized to work", "right to work in india"]):
        return "Yes"

    if any(k in q for k in ["sponsorship", "require visa", "visa support"]):
        return "No"

    if any(k in q for k in ["relocate", "willing to move"]):
        return "Yes"

    if any(k in q for k in ["hybrid", "remote", "comfortable working"]):
        return "Yes"

    if any(k in q for k in ["phone", "mobile", "contact number"]):
        return profile.get("phone", "+91 9876543210")

    if any(k in q for k in ["linkedin", "profile link"]):
        return profile.get("linkedin_url", "")

    if any(k in q for k in ["github", "git profile"]):
        return profile.get("github_url", "")

    # 3. Technical Skill Experience Questions ("How many years of Python experience do you have?")
    if "years of experience" in q or "how many years" in q:
        # Check if question mentions any skill in resume
        if resume_skills:
            for skill in resume_skills:
                if skill.lower() in q:
                    return str(min(experience_years, 5))
        return str(experience_years)

    return None
