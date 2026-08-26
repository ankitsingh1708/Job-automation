import os
import uuid
import re
import time
import threading
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Browser, Page

from app.services.profile_store import load_profile, record_question_answer, lookup_known_answer

class AutoApplySession:
    def __init__(self, session_id: str, job_id: str, job_title: str, company_name: str, apply_url: str):
        self.session_id = session_id
        self.job_id = job_id
        self.job_title = job_title
        self.company_name = company_name
        self.apply_url = apply_url
        self.status = "INITIALIZING"
        self.logs: List[str] = []
        self.pending_question: Optional[Dict[str, Any]] = None
        self.user_answer: Optional[str] = None
        self.answer_event = threading.Event()
        self.created_at = datetime.now()
        self.error_message: Optional[str] = None
        self.is_active = True

    def log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{ts}] {message}")

ACTIVE_SESSIONS: Dict[str, AutoApplySession] = {}

def get_session(session_id: str) -> Optional[AutoApplySession]:
    return ACTIVE_SESSIONS.get(session_id)

def answer_session_question(session_id: str, answer: str) -> bool:
    session = ACTIVE_SESSIONS.get(session_id)
    if not session or session.status != "WAITING_FOR_USER_INPUT":
        return False

    session.user_answer = answer
    if session.pending_question:
        q_text = session.pending_question.get("question", "")
        record_question_answer(q_text, answer)
        session.log(f"Answer received from user: '{answer}' (Saved to memory)")

    session.pending_question = None
    session.answer_event.set()
    return True

def start_auto_apply_task(
    job_id: str,
    job_title: str,
    company_name: str,
    apply_url: str,
    resume_path: Optional[str] = None,
    candidate_skills: Optional[List[str]] = None,
    experience_years: int = 4,
    headless: bool = False
) -> str:
    session_id = str(uuid.uuid4())[:8]
    session = AutoApplySession(
        session_id=session_id,
        job_id=job_id,
        job_title=job_title,
        company_name=company_name,
        apply_url=apply_url
    )
    ACTIVE_SESSIONS[session_id] = session

    # Run in dedicated thread for Windows & Uvicorn stability
    worker_thread = threading.Thread(
        target=_run_sync_playwright_apply,
        args=(session, resume_path, candidate_skills or [], experience_years, headless),
        daemon=True
    )
    worker_thread.start()

    return session_id

def _run_sync_playwright_apply(
    session: AutoApplySession,
    resume_path: Optional[str],
    candidate_skills: List[str],
    experience_years: int,
    headless: bool
):
    profile = load_profile()
    session.status = "CONNECTING"
    session.log(f"Starting Auto-Apply agent for '{session.job_title}' at {session.company_name}")

    try:
        with sync_playwright() as p:
            session.log("Launching Chromium browser window...")
            browser = p.chromium.launch(
                headless=headless,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 850},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            session.status = "OPENING_PORTAL"
            session.log(f"Navigating to job URL: {session.apply_url}")
            page.goto(session.apply_url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(3)

            session.status = "FILLING_FORM"
            session.log("Scanning page structure for application inputs...")

            # 1. Look for Easy Apply or Apply buttons
            easy_apply_btn = page.locator("button:has-text('Easy Apply'), button.jobs-apply-button, a:has-text('Apply')").first
            if easy_apply_btn.count() > 0 and easy_apply_btn.is_visible():
                session.log("Found 'Easy Apply' button. Clicking...")
                try:
                    easy_apply_btn.click()
                    time.sleep(2)
                except Exception as ce:
                    session.log(f"Click note: {ce}")
            else:
                session.log("Direct application form detected on page.")

            # Multi-step Form Processing
            max_steps = 8
            for step in range(1, max_steps + 1):
                session.log(f"Processing application Step {step}...")

                # A. Handle Text, Email, Phone, Number Inputs
                inputs = page.locator("input[type='text'], input[type='tel'], input[type='email'], input[type='number'], textarea")
                input_count = inputs.count()

                for i in range(input_count):
                    inp = inputs.nth(i)
                    if not inp.is_visible():
                        continue

                    label_text = _get_input_label(page, inp)
                    current_val = inp.input_value()

                    if not current_val:
                        known_ans = lookup_known_answer(label_text, candidate_skills, experience_years)

                        if known_ans:
                            session.log(f"Auto-filling field '{label_text}' -> {known_ans}")
                            try:
                                inp.fill(str(known_ans))
                            except Exception:
                                pass
                        else:
                            # Prompt user in web UI!
                            session.status = "WAITING_FOR_USER_INPUT"
                            session.pending_question = {
                                "question": label_text or "Please provide the required details",
                                "field_type": "text",
                                "suggested_answer": ""
                            }
                            session.log(f"❓ Prompting recruiter question: '{label_text}'")
                            session.answer_event.clear()

                            # Wait up to 3 minutes for user input
                            answered = session.answer_event.wait(timeout=180)
                            if answered and session.user_answer:
                                try:
                                    inp.fill(str(session.user_answer))
                                except Exception:
                                    pass
                            session.status = "FILLING_FORM"

                # B. Handle Radio Buttons & Fieldsets (e.g. Yes/No questions)
                fieldsets = page.locator("fieldset")
                fs_count = fieldsets.count()
                for f_idx in range(fs_count):
                    fs = fieldsets.nth(f_idx)
                    legend = fs.locator("legend").text_content() if fs.locator("legend").count() > 0 else ""
                    legend_clean = legend.strip() if legend else ""

                    if legend_clean:
                        known_ans = lookup_known_answer(legend_clean, candidate_skills, experience_years)
                        if known_ans:
                            target_radio = fs.locator(f"label:has-text('{known_ans}')").first
                            if target_radio.count() > 0:
                                try:
                                    target_radio.click()
                                    session.log(f"Selected option for '{legend_clean}' -> {known_ans}")
                                except Exception:
                                    pass
                        else:
                            session.status = "WAITING_FOR_USER_INPUT"
                            session.pending_question = {
                                "question": legend_clean,
                                "field_type": "choice",
                                "options": ["Yes", "No"]
                            }
                            session.log(f"❓ Prompting choice: '{legend_clean}'")
                            session.answer_event.clear()
                            answered = session.answer_event.wait(timeout=180)
                            if answered and session.user_answer:
                                target_radio = fs.locator(f"label:has-text('{session.user_answer}')").first
                                if target_radio.count() > 0:
                                    try:
                                        target_radio.click()
                                    except Exception:
                                        pass
                            session.status = "FILLING_FORM"

                # C. Handle File Upload / Resume
                file_input = page.locator("input[type='file']").first
                if file_input.count() > 0 and resume_path and os.path.exists(resume_path):
                    try:
                        session.log("Attaching resume PDF...")
                        file_input.set_input_files(resume_path)
                        session.log("✅ Resume attached.")
                    except Exception as fe:
                        session.log(f"File upload note: {fe}")

                time.sleep(1)

                # D. Check for Next / Review / Submit Button
                next_btn = page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Review')").first
                submit_btn = page.locator("button:has-text('Submit application'), button:has-text('Submit'), button:has-text('Apply now')").first

                if submit_btn.count() > 0 and submit_btn.is_visible():
                    session.status = "REVIEW_READY"
                    session.log("🎉 Application details populated and ready for review!")
                    session.log("You can review entries in the browser window and click Submit.")
                    break
                elif next_btn.count() > 0 and next_btn.is_visible():
                    session.log("Clicking 'Next' step...")
                    try:
                        next_btn.click()
                        time.sleep(2)
                    except Exception:
                        break
                else:
                    session.status = "REVIEW_READY"
                    session.log("All visible fields populated. Ready for review.")
                    break

            # Keep browser alive for user to inspect/submit
            for _ in range(30):
                if not session.is_active:
                    break
                time.sleep(5)

            browser.close()

    except Exception as e:
        session.status = "ERROR"
        session.error_message = f"{str(e)}\n{traceback.format_exc()}"
        session.log(f"Auto-Apply note: {e}")

def _get_input_label(page: Page, input_locator) -> str:
    try:
        aria_label = input_locator.get_attribute("aria-label")
        if aria_label and aria_label.strip():
            return aria_label.strip()

        placeholder = input_locator.get_attribute("placeholder")
        if placeholder and placeholder.strip():
            return placeholder.strip()

        inp_id = input_locator.get_attribute("id")
        if inp_id:
            label = page.locator(f"label[for='{inp_id}']").first
            if label.count() > 0:
                txt = label.text_content()
                if txt and txt.strip():
                    return txt.strip()

        parent_text = input_locator.evaluate("el => el.closest('div, label, fieldset')?.innerText || ''")
        first_line = parent_text.split("\n")[0].strip() if parent_text else ""
        if first_line and len(first_line) < 100:
            return first_line

        name_attr = input_locator.get_attribute("name")
        return name_attr or "Input Field"
    except Exception:
        return "Input Field"
