import re
from typing import List, Dict, Any, Set

# Indian IT Service Giants & Mid-tier Outsourcing Firms
INDIAN_SERVICE_COMPANIES: Set[str] = {
    # Top Tier Service Giants
    "accenture",
    "accenture in india",
    "accenture baltics",
    "accenture song",
    "accenture interactive",
    "accenture solutions",
    "tcs",
    "tata consultancy services",
    "infosys",
    "infosys bpm",
    "wipro",
    "wipro limited",
    "wipro technologies",
    "cognizant",
    "cognizant technology solutions",
    "cts",
    "hcl",
    "hcltech",
    "hcl technologies",
    "tech mahindra",
    "mahindra satyam",
    "capgemini",
    "ltimindtree",
    "mindtree",
    "larsen & toubro infotech",
    "lti",
    "l&t infotech",
    "l&t technology services",
    "ltts",

    # Mid-Tier Service & IT Outsourcers
    "hexaware",
    "hexaware technologies",
    "mphasis",
    "birlasoft",
    "persistent",
    "persistent systems",
    "ust",
    "ust global",
    "cyient",
    "tata elxsi",
    "sonata software",
    "zensar",
    "zensar technologies",
    "kpit",
    "kpit technologies",
    "coforge",
    "niit technologies",
    "genpact",
    "exl",
    "exl service",
    "wns",
    "wns global services",
    "itc infotech",
    "syntel",
    "atos syntel",
    "atos",
    "sutherland",
    "sutherland global",
    "datamatics",
    "3i infotech",
    "happiest minds",
    "happiest minds technologies",
    "brillio",
    "quest global",
    "citiustech",
    "virtusa",
    "virtusa corporation",
    "nagarro",
    "apexon",
    "infostretch",
    "kellton",
    "kellton tech",
    "sasken",
    "sasken technologies",
    "cigniti",
    "cigniti technologies",
    "mindgate solutions",
    "newgen software",
    "infogain",
    "clover infotech",
    "aspire systems",
    "accolite",
    "accolite digital",
    "globallogic",
    "dxc technology",
    "ntt data",
    "cgi",
    "mu sigma",
    "latentview analytics",

    # Staffing Agencies & Body Shoppers
    "collabera",
    "teamlease",
    "teamlease digital",
    "quess corp",
    "quess",
    "randstad",
    "randstad india",
    "adecco",
    "adecco india",
    "kelly services",
    "teksystems",
    "allegis group",
    "actalent",
    "aerotek",
    "experis",
    "manpowergroup",
    "idc technologies",
    "synechron",
    "disys",
    "kforce",
    "pyramid consulting",
    "artech information systems",
    "us tech solutions",
    "lancesoft",
    "cynet systems",
    "vdart",
    "infobeans",
    "emonics",
    "rang technologies"
}

# 🌟 High-Pay Top Product Companies & Unicorns (30+ LPA for SDE-2)
TOP_TIER_COMPANIES: Set[str] = {
    # FAANG / Silicon Valley Leaders
    "google", "microsoft", "amazon", "aws", "amazon web services", "meta", "apple",
    "uber", "atlassian", "adobe", "salesforce", "netflix", "stripe", "databricks",
    "snowflake", "coinbase", "rippling", "linkedin", "intuit", "oracle", "oci",
    "nutanix", "rubrik", "cohesity", "palo alto networks", "servicenow", "twilio",
    "vmware", "broadcom", "hackerrank", "github", "pinterest", "airbnb", "doordash",

    # Top Indian Unicorns & High-Pay Scale-ups
    "cred", "swiggy", "flipkart", "razorpay", "zomato", "blinkit", "zepto", "phonepe",
    "groww", "dream11", "dream sports", "fancode", "media.net", "inmobi", "glance",
    "zeta", "directi", "slice", "tekion", "tekion corp", "sharechat", "moj",
    "navi", "navi technologies", "browserstack", "postman", "meesho", "udaan",
    "urban company", "nykaa", "paytm", "lenskart", "spinny", "cars24", "ola",

    # Quant, HFT & Top FinTech GCCs
    "de shaw", "d. e. shaw", "d.e. shaw", "arcesium", "goldman sachs", "morgan stanley",
    "jpmorgan", "jpmorganchase", "j.p. morgan", "millennium", "millennium management",
    "tower research", "tower research capital", "graviton", "graviton research",
    "worldquant", "citadel", "citadel securities", "hudson river trading", "hrt",
    "jane street", "quadeye", "drw", "jump trading", "twosigma", "two sigma",

    # Global Enterprise Cloud & Consumer Product Leaders
    "walmart", "walmart global tech", "expedia", "expedia group", "target",
    "target technology services", "cisco", "paypal", "workday", "qualtrics",
    "mastercard", "visa", "booking.com", "grab", "airtel digital", "jio"
}

SERVICE_PATTERNS = [
    re.compile(r'\b(tata consultancy|tcs|infosys|wipro|cognizant|hcltech|hcl technologies|tech mahindra)\b', re.IGNORECASE),
    re.compile(r'\b(ltimindtree|mindtree|hexaware|mphasis|birlasoft|persistent systems|ust global)\b', re.IGNORECASE),
    re.compile(r'\b(tata elxsi|sonata software|zensar|kpit|coforge|genpact|virtusa|nagarro)\b', re.IGNORECASE),
    re.compile(r'\b(itc infotech|sutherland global|happiest minds|brillio|quest global|citiustech)\b', re.IGNORECASE),
    re.compile(r'\b(collabera|teamlease|quess corp|teksystems|pyramid consulting|idc technologies)\b', re.IGNORECASE),
    re.compile(r'\b(infotech|technologies limited|it consultancy|staffing solutions|manpower services)\b', re.IGNORECASE),
]

TOP_TIER_PATTERNS = [
    re.compile(r'\b(google|microsoft|amazon|uber|atlassian|adobe|salesforce|stripe|databricks|snowflake|coinbase|rippling)\b', re.IGNORECASE),
    re.compile(r'\b(cred|swiggy|flipkart|razorpay|zomato|blinkit|zepto|phonepe|groww|dream11|media\.net|inmobi|zeta|tekion)\b', re.IGNORECASE),
    re.compile(r'\b(de shaw|arcesium|goldman sachs|morgan stanley|jpmorgan|walmart|servicenow|nutanix|rubrik|cohesity)\b', re.IGNORECASE),
]

def clean_company_name(name: str) -> str:
    if not name:
        return ""
    clean = name.lower().strip()
    clean = re.sub(r'[\(\)\[\],.\-\/]', ' ', clean)
    clean = re.sub(r'\b(pvt|ltd|limited|inc|corp|corporation|llc|gmbh|co|services|technologies|solutions|india|global)\b', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def is_service_company(company_name: str) -> bool:
    if not company_name:
        return False
    raw_lower = company_name.lower().strip()
    normalized = clean_company_name(company_name)

    if raw_lower in INDIAN_SERVICE_COMPANIES or normalized in INDIAN_SERVICE_COMPANIES:
        return True

    for target in INDIAN_SERVICE_COMPANIES:
        if target in raw_lower or target in normalized:
            return True

    for pattern in SERVICE_PATTERNS:
        if pattern.search(raw_lower):
            return True

    return False

def is_top_tier_company(company_name: str) -> bool:
    """
    Checks if a company is in the 30+ LPA Top Tier registry (FAANG, Top Unicorns, FinTech & GCCs).
    """
    if not company_name:
        return False
    raw_lower = company_name.lower().strip()
    normalized = clean_company_name(company_name)

    if raw_lower in TOP_TIER_COMPANIES or normalized in TOP_TIER_COMPANIES:
        return True

    for target in TOP_TIER_COMPANIES:
        if target in raw_lower or target in normalized:
            return True

    for pattern in TOP_TIER_PATTERNS:
        if pattern.search(raw_lower):
            return True

    return False

def filter_jobs_by_company(
    jobs: List[Dict[str, Any]],
    exclude_service: bool = False,
    top_tier_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Filters and tags jobs with is_service_company and is_top_tier.
    """
    filtered = []
    for job in jobs:
        comp_name = job.get('company_name', '')
        is_svc = is_service_company(comp_name)
        is_tier1 = is_top_tier_company(comp_name)

        job['is_service_company'] = is_svc
        job['is_top_tier'] = is_tier1

        if exclude_service and is_svc:
            continue

        if top_tier_only and not is_tier1:
            continue

        filtered.append(job)
    return filtered
