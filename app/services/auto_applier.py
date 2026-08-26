import os
import uuid
import re
import time
import threading
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

from app.services.profile_store import load_profile, record_question_answer, lookup_known_answer

# Persistent Chrome Profile directory so LinkedIn login session stays preserved
CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "services", ".chrome_profile")
os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)

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
            session.log("Opening dedicated Chrome window with persistent login session...")
            
            context = None
            try:
                # Launch persistent Chrome browser window
                context = p.chromium.launch_persistent_context(
                    user_data_dir=CHROME_PROFILE_DIR,
                    channel="chrome",
                    headless=headless,
                    no_viewport=True,
                    args=[
                        "--start-maximized",
                        "--disable-blink-features=AutomationControlled",
                        "--window-size=1280,850",
                        "--window-position=50,50"
                    ]
                )
            except Exception:
                # Fallback to Chromium persistent context
                context = p.chromium.launch_persistent_context(
                    user_data_dir=CHROME_PROFILE_DIR,
                    headless=headless,
                    no_viewport=True,
                    args=[
                        "--start-maximized",
                        "--disable-blink-features=AutomationControlled",
                        "--window-size=1280,850",
                        "--window-position=50,50"
                    ]
                )

            active_page = context.pages[0] if context.pages else context.new_page()

            # Handle new tabs/popups
            def handle_new_page(new_p: Page):
                nonlocal active_page
                session.log(f"Switched to application tab: {new_p.url[:60]}...")
                active_page = new_p
                try:
                    active_page.bring_to_front()
                except Exception:
                    pass

            context.on("page", handle_new_page)

            session.status = "OPENING_PORTAL"
            session.log(f"Navigating to job URL: {session.apply_url}")
            active_page.goto(session.apply_url, wait_until="domcontentloaded", timeout=45000)
            active_page.bring_to_front()
            time.sleep(3)

            # Check if user needs to log into LinkedIn once
            sign_in_prompt = active_page.locator("a:has-text('Sign in'), button:has-text('Sign in')").first
            if sign_in_prompt.count() > 0 and sign_in_prompt.is_visible():
                session.log("💡 Tip: If prompted to Sign In to LinkedIn in the Chrome window, log in once — your session will be saved permanently!")

            # 1. Look for and click Easy Apply or Apply on Company Website button
            session.log("Checking for Apply action buttons...")
            apply_btn = active_page.locator("button.jobs-apply-button, a.apply-button, button:has-text('Easy Apply'), a:has-text('Apply on company website'), a:has-text('Apply'), button:has-text('Apply')").first

            if apply_btn.count() > 0 and apply_btn.is_visible():
                btn_text = apply_btn.inner_text().strip()
                session.log(f"Clicking '{btn_text}' button...")
                try:
                    apply_btn.click()
                    time.sleep(3)
                except Exception as ce:
                    session.log(f"Click notice: {ce}")
            
            # Switch to newest page if popup opened
            if len(context.pages) > 1:
                active_page = context.pages[-1]
                active_page.bring_to_front()
                session.log(f"Switched to application portal tab: {active_page.url[:60]}")

            session.status = "FILLING_FORM"
            session.log("Scanning page structure for interactive application fields...")

            # Multi-step Form Processing Loop
            max_steps = 10
            form_fields_found_total = 0

            for step in range(1, max_steps + 1):
                session.log(f"Processing application Step {step}...")
                active_page.bring_to_front()

                # A. Handle Text, Email, Phone, Number Inputs
                inputs = active_page.locator("input[type='text'], input[type='tel'], input[type='email'], input[type='number'], textarea")
                input_count = inputs.count()

                if input_count > 0:
                    form_fields_found_total += input_count

                for i in range(input_count):
                    inp = inputs.nth(i)
                    if not inp.is_visible():
                        continue

                    label_text = _get_input_label(active_page, inp)
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

                            answered = session.answer_event.wait(timeout=180)
                            if answered and session.user_answer:
                                try:
                                    inp.fill(str(session.user_answer))
                                except Exception:
                                    pass
                            session.status = "FILLING_FORM"

                # B. Handle Radio Buttons & Fieldsets (Yes/No questions)
                fieldsets = active_page.locator("fieldset")
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
                file_input = active_page.locator("input[type='file']").first
                if file_input.count() > 0 and resume_path and os.path.exists(resume_path):
                    try:
                        session.log("Attaching resume PDF...")
                        file_input.set_input_files(resume_path)
                        session.log("✅ Resume attached.")
                    except Exception as fe:
                        session.log(f"File upload note: {fe}")

                time.sleep(1)

                # D. Check for Next / Review / Submit Button
                next_btn = active_page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Review')").first
                submit_btn = active_page.locator("button:has-text('Submit application'), button:has-text('Submit'), button:has-text('Apply now')").first

                if submit_btn.count() > 0 and submit_btn.is_visible():
                    session.status = "REVIEW_READY"
                    session.log("🎉 Application details populated and ready for review!")
                    session.log("You can review entries in the Chrome window and click Submit.")
                    break
                elif next_btn.count() > 0 and next_btn.is_visible():
                    session.log("Clicking 'Next' step...")
                    try:
                        next_btn.click()
                        time.sleep(2)
                    except Exception:
                        break
                else:
                    if form_fields_found_total > 0:
                        session.status = "REVIEW_READY"
                        session.log("All visible fields populated. Ready for review.")
                    else:
                        session.status = "REVIEW_READY"
                        session.log("Application portal is open in your Chrome window.")
                        session.log("You can review and complete any company-specific verification directly in the Chrome window!")
                    break

            # Keep Chrome open for up to 5 minutes
            for _ in range(60):
                if not session.is_active:
                    break
                time.sleep(5)

            context.close()

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
