import asyncio
import os
import uuid
import re
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page

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
        self.answer_event = asyncio.Event()
        self.created_at = datetime.now()
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.error_message: Optional[str] = None

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

async def start_auto_apply_task(
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

    asyncio.create_task(
        _run_playwright_apply(
            session=session,
            resume_path=resume_path,
            candidate_skills=candidate_skills or [],
            experience_years=experience_years,
            headless=headless
        )
    )

    return session_id

async def _run_playwright_apply(
    session: AutoApplySession,
    resume_path: Optional[str],
    candidate_skills: List[str],
    experience_years: int,
    headless: bool
):
    profile = load_profile()
    session.status = "CONNECTING"
    session.log(f"Starting Auto-Apply engine for '{session.job_title}' at {session.company_name}")

    try:
        async with async_playwright() as p:
            session.log("Launching Chromium browser session...")
            browser = await p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            session.browser = browser

            context = await browser.new_context(
                viewport={"width": 1280, "height": 850},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            session.page = page

            session.status = "OPENING_PORTAL"
            session.log(f"Navigating to: {session.apply_url}")
            await page.goto(session.apply_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)

            session.status = "FILLING_FORM"
            session.log("Scanning page structure for application inputs...")

            # 1. Try to find Easy Apply button or Apply button
            easy_apply_btn = page.locator("button:has-text('Easy Apply'), button.jobs-apply-button, a:has-text('Apply')").first
            if await easy_apply_btn.count() > 0 and await easy_apply_btn.is_visible():
                session.log("Found 'Easy Apply' button. Clicking...")
                await easy_apply_btn.click()
                await asyncio.sleep(2)
            else:
                session.log("Direct application form detected on page.")

            # Multi-step form loop
            max_steps = 8
            for step in range(1, max_steps + 1):
                session.log(f"Processing application Step {step}...")

                # 1. Fill Text Inputs & Phone / Email / Name
                inputs = page.locator("input[type='text'], input[type='tel'], input[type='email'], input[type='number'], textarea")
                input_count = await inputs.count()

                for i in range(input_count):
                    inp = inputs.nth(i)
                    if not await inp.is_visible():
                        continue

                    label_text = await _get_input_label(page, inp)
                    current_val = await inp.input_value()

                    if not current_val:
                        known_ans = lookup_known_answer(label_text, candidate_skills, experience_years)

                        if known_ans:
                            session.log(f"Auto-filling field '{label_text}' -> {known_ans}")
                            await inp.fill(str(known_ans))
                        else:
                            # Prompt user in UI!
                            session.status = "WAITING_FOR_USER_INPUT"
                            session.pending_question = {
                                "question": label_text or "Please fill required field",
                                "field_type": "text",
                                "suggested_answer": ""
                            }
                            session.log(f"❓ Prompting user: '{label_text}'")
                            session.answer_event.clear()

                            await session.answer_event.wait()
                            user_ans = session.user_answer or ""
                            await inp.fill(user_ans)
                            session.status = "FILLING_FORM"

                # 2. Handle Radio Buttons & Yes/No Questions
                fieldsets = page.locator("fieldset")
                fs_count = await fieldsets.count()
                for f_idx in range(fs_count):
                    fs = fieldsets.nth(f_idx)
                    legend = await fs.locator("legend").text_content() if await fs.locator("legend").count() > 0 else ""
                    legend_clean = legend.strip() if legend else ""

                    if legend_clean:
                        known_ans = lookup_known_answer(legend_clean, candidate_skills, experience_years)
                        if known_ans:
                            target_radio = fs.locator(f"label:has-text('{known_ans}')").first
                            if await target_radio.count() > 0:
                                await target_radio.click()
                                session.log(f"Selected radio option for '{legend_clean}' -> {known_ans}")
                        else:
                            session.status = "WAITING_FOR_USER_INPUT"
                            session.pending_question = {
                                "question": legend_clean,
                                "field_type": "choice",
                                "options": ["Yes", "No"]
                            }
                            session.log(f"❓ Prompting choice: '{legend_clean}'")
                            session.answer_event.clear()
                            await session.answer_event.wait()

                            user_ans = session.user_answer or "Yes"
                            target_radio = fs.locator(f"label:has-text('{user_ans}')").first
                            if await target_radio.count() > 0:
                                await target_radio.click()
                            session.status = "FILLING_FORM"

                # 3. Check for File Upload / Resume PDF
                file_input = page.locator("input[type='file']").first
                if await file_input.count() > 0 and resume_path and os.path.exists(resume_path):
                    try:
                        session.log("Uploading resume PDF attachment...")
                        await file_input.set_input_files(resume_path)
                        session.log("✅ Resume attached successfully.")
                    except Exception as fe:
                        session.log(f"File upload note: {fe}")

                await asyncio.sleep(1)

                # 4. Check for Next / Review / Submit Button
                next_btn = page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Review')").first
                submit_btn = page.locator("button:has-text('Submit application'), button:has-text('Submit'), button:has-text('Apply now')").first

                if await submit_btn.count() > 0 and await submit_btn.is_visible():
                    session.status = "REVIEW_READY"
                    session.log("🎉 Application details fully populated and ready for review!")
                    session.log("You can review the entries in the browser window and click Submit.")
                    break
                elif await next_btn.count() > 0 and await next_btn.is_visible():
                    session.log("Clicking 'Next' step...")
                    await next_btn.click()
                    await asyncio.sleep(2)
                else:
                    session.status = "REVIEW_READY"
                    session.log("All visible fields populated. Ready for final review.")
                    break

            try:
                await asyncio.sleep(180)
            except asyncio.CancelledError:
                pass

    except Exception as e:
        session.status = "ERROR"
        session.error_message = f"{str(e)}\n{traceback.format_exc()}"
        session.log(f"Auto-Apply session finished: {e}")

async def _get_input_label(page: Page, input_locator) -> str:
    try:
        aria_label = await input_locator.get_attribute("aria-label")
        if aria_label and aria_label.strip():
            return aria_label.strip()

        placeholder = await input_locator.get_attribute("placeholder")
        if placeholder and placeholder.strip():
            return placeholder.strip()

        inp_id = await input_locator.get_attribute("id")
        if inp_id:
            label = page.locator(f"label[for='{inp_id}']").first
            if await label.count() > 0:
                txt = await label.text_content()
                if txt and txt.strip():
                    return txt.strip()

        parent_text = await input_locator.evaluate("el => el.closest('div, label, fieldset')?.innerText || ''")
        first_line = parent_text.split("\n")[0].strip() if parent_text else ""
        if first_line and len(first_line) < 100:
            return first_line

        name_attr = await input_locator.get_attribute("name")
        return name_attr or "Input Field"
    except Exception:
        return "Input Field"
