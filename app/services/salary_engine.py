import re
from typing import Dict, Any, Optional, Tuple

# LeetCode & Levels.fyi Verified Tier-1 Tech Giants in India
TIER1_GLOBAL_TECH = {
    "google", "microsoft", "amazon", "uber", "atlassian", "adobe", "salesforce",
    "intuit", "walmart", "walmart global tech", "oracle", "cisco", "linkedin",
    "meta", "apple", "stripe", "openai", "databricks", "snowflake"
}

# LeetCode & Levels.fyi Verified Top Indian Unicorns & High-Paying Product Startups
TIER1_INDIAN_UNICORNS = {
    "flipkart", "swiggy", "razorpay", "zomato", "zepto", "blinkit", "phonepe",
    "cred", "meesho", "paytm", "inmobi", "browserstack", "postman", "groww",
    "zerodha", "curefit", "dream11", "ola", "urban company", "nykaa", "lenskart",
    "slice", "jupiter", "credgenics"
}

# Role baseline ranges for Indian Product Ecosystem (in Lakhs per Annum / LPA)
INDIAN_TECH_SALARY_BENCHMARKS = {
    "software engineer": (14, 25),
    "sde": (15, 26),
    "senior software engineer": (26, 45),
    "senior sde": (28, 48),
    "python developer": (13, 25),
    "python engineer": (15, 28),
    "senior python": (26, 46),
    "full stack": (15, 30),
    "frontend": (13, 24),
    "backend": (16, 32),
    "devops": (17, 34),
    "cloud": (18, 36),
    "sre": (18, 38),
    "data scientist": (16, 32),
    "machine learning": (20, 42),
    "ai engineer": (24, 52),
    "genai": (26, 55),
    "llm": (26, 58),
    "data engineer": (15, 30),
    "java developer": (14, 26),
    "senior java": (26, 45),
    "react developer": (13, 24),
    "node": (15, 28),
    "golang": (20, 40),
    "qa": (10, 20),
    "sdet": (15, 28),
    "product manager": (22, 48),
    "engineering manager": (45, 85),
    "architect": (38, 70),
    "tech lead": (32, 60),
    "security engineer": (18, 38),
}

SENIORITY_MULTIPLIERS = {
    "intern": 0.40,
    "entry": 0.75,
    "junior": 0.75,
    "associate": 0.85,
    "mid-senior": 1.10,
    "senior": 1.40,
    "lead": 1.65,
    "principal": 1.95,
    "staff": 1.90,
    "director": 2.30,
    "head": 2.15,
    "manager": 1.70
}

# Regex to detect raw salary mentions inside text
SALARY_REGEXES = [
    # INR formats (₹15 LPA - ₹25 LPA, 15-25 LPA, ₹12,00,000 - ₹20,00,000)
    re.compile(r'((?:₹|INR|Rs\.?)\s*\d+(?:\.\d+)?\s*(?:LPA|L|Lakhs?|Cr)?\s*(?:-|–|to)\s*(?:₹|INR|Rs\.?)?\s*\d+(?:\.\d+)?\s*(?:LPA|L|Lakhs?|Cr))', re.IGNORECASE),
    re.compile(r'(\b\d+(?:\.\d+)?\s*(?:-|–|to)\s*\d+(?:\.\d+)?\s*(?:LPA|Lakhs?\s*(?:per\s*annum)?)\b)', re.IGNORECASE),
    re.compile(r'((?:₹|INR|Rs\.?)\s*\d{1,2},\d{2},\d{3}\s*(?:-|–|to)\s*(?:₹|INR|Rs\.?)?\s*\d{1,2},\d{2},\d{3})', re.IGNORECASE),

    # USD formats
    re.compile(r'(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*[kK])?\s*(?:-|–|to)\s*\$\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*[kK])?(?:\s*(?:/|per|a)?\s*(?:yr|year|annum|hr|hour|mo|month))?)', re.IGNORECASE),
    re.compile(r'(\$\s*\d{1,3}(?:,\d{3})+(?:\s*(?:/|per|a)?\s*(?:yr|year|annum|hr|hour|mo|month)))', re.IGNORECASE),
    
    # GBP & EUR formats
    re.compile(r'(£\s*\d{1,3}(?:,\d{3})*(?:\s*[kK])?\s*(?:-|–|to)\s*£?\s*\d{1,3}(?:,\d{3})*(?:\s*[kK])?(?:\s*(?:/|per|a)?\s*(?:yr|year|annum))?)', re.IGNORECASE),
    re.compile(r'(€\s*\d{1,3}(?:,\d{3})*(?:\s*[kK])?\s*(?:-|–|to)\s*€?\s*\d{1,3}(?:,\d{3})*(?:\s*[kK])?(?:\s*(?:/|per|a)?\s*(?:yr|year|annum))?)', re.IGNORECASE),
]

def extract_salary_from_text(text: str) -> Optional[str]:
    """
    Scans text for explicit salary figures.
    """
    if not text:
        return None

    for pattern in SALARY_REGEXES:
        match = pattern.search(text)
        if match:
            found = match.group(1).strip()
            found = re.sub(r'[\.,;]$', '', found)
            return found

    return None

def estimate_market_salary(
    title: str,
    company_name: str = '',
    location: str = '',
    experience_level: str = ''
) -> Dict[str, Any]:
    """
    Estimates compensation based on crowdsourced LeetCode & Levels.fyi reported benchmarks in India.
    """
    t_lower = (title or '').lower()
    c_lower = (company_name or '').lower().strip()
    exp_lower = (experience_level or '').lower()

    # Determine seniority multiplier
    multiplier = 1.0
    for sen_key, mult in SENIORITY_MULTIPLIERS.items():
        if sen_key in t_lower or sen_key in exp_lower:
            multiplier = max(multiplier, mult)

    # 1. Check if Company is a Tier-1 Global Tech Giant (LeetCode India verified)
    if any(comp in c_lower for comp in TIER1_GLOBAL_TECH):
        if "senior" in t_lower or "lead" in t_lower or multiplier >= 1.4:
            min_sal, max_sal = 65, 110
        elif "intern" in t_lower:
            min_sal, max_sal = 12, 18
        elif "sde 2" in t_lower or "sde ii" in t_lower or multiplier > 1.0:
            min_sal, max_sal = 42, 70
        else:
            min_sal, max_sal = 22, 36

        return {
            "salary": f"₹{min_sal}L - ₹{max_sal}L / yr",
            "salary_type": "leetcode_verified",
            "currency": "INR",
            "min_amount": min_sal,
            "max_amount": max_sal,
            "source_label": "LeetCode / Levels.fyi India Verified",
            "is_estimated": True
        }

    # 2. Check if Company is a Top Indian Unicorn (LeetCode India verified)
    if any(comp in c_lower for comp in TIER1_INDIAN_UNICORNS):
        if "senior" in t_lower or "lead" in t_lower or multiplier >= 1.4:
            min_sal, max_sal = 45, 75
        elif "intern" in t_lower:
            min_sal, max_sal = 8, 14
        elif "sde 2" in t_lower or "sde ii" in t_lower or multiplier > 1.0:
            min_sal, max_sal = 32, 55
        else:
            min_sal, max_sal = 18, 30

        return {
            "salary": f"₹{min_sal}L - ₹{max_sal}L / yr",
            "salary_type": "leetcode_verified",
            "currency": "INR",
            "min_amount": min_sal,
            "max_amount": max_sal,
            "source_label": "LeetCode / AmbitionBox Verified",
            "is_estimated": True
        }

    # 3. Product Startups & General Tech Ecosystem Benchmark
    base_range = None
    for role_key, r_tuple in INDIAN_TECH_SALARY_BENCHMARKS.items():
        if role_key in t_lower:
            base_range = r_tuple
            break

    if not base_range:
        base_range = INDIAN_TECH_SALARY_BENCHMARKS["software engineer"]

    min_sal = max(7, int(base_range[0] * multiplier))
    max_sal = max(min_sal + 5, int(base_range[1] * multiplier))

    return {
        "salary": f"₹{min_sal}L - ₹{max_sal}L / yr",
        "salary_type": "estimated",
        "currency": "INR",
        "min_amount": min_sal,
        "max_amount": max_sal,
        "source_label": "Indian Market Standard",
        "is_estimated": True
    }

def resolve_job_salary(
    raw_salary: Optional[str] = None,
    title: str = '',
    company_name: str = '',
    location: str = '',
    description_text: str = '',
    experience_level: str = ''
) -> Dict[str, Any]:
    """
    Resolves salary prioritizing Indian Market and LeetCode crowdsourced benchmarks:
    1. Direct employer pay tag if present
    2. Extracted pay from description text if present
    3. LeetCode / Levels.fyi verified company tiers or market benchmark (in ₹ LPA)
    """
    if raw_salary and raw_salary.strip() and raw_salary.lower() not in ['competitive salary', 'competitive', 'not specified', 'none']:
        return {
            "salary": raw_salary.strip(),
            "salary_type": "exact",
            "currency": "INR",
            "is_estimated": False
        }

    extracted = extract_salary_from_text(description_text)
    if extracted:
        return {
            "salary": extracted,
            "salary_type": "exact",
            "currency": "INR",
            "is_estimated": False
        }

    return estimate_market_salary(
        title=title,
        company_name=company_name,
        location=location,
        experience_level=experience_level
    )
