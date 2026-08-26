import re
from typing import List, Dict, Any, Set

# Indian IT Service Giants & Mid-tier Outsourcing Firms
INDIAN_SERVICE_COMPANIES: Set[str] = {
    # Top Tier
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

    # Common Contract / Body Shopping Staffing Agencies
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

# Regex patterns matching variations and staffing keywords
SERVICE_PATTERNS = [
    re.compile(r'\b(tata consultancy|tcs|infosys|wipro|cognizant|hcltech|hcl technologies|tech mahindra)\b', re.IGNORECASE),
    re.compile(r'\b(ltimindtree|mindtree|hexaware|mphasis|birlasoft|persistent systems|ust global)\b', re.IGNORECASE),
    re.compile(r'\b(tata elxsi|sonata software|zensar|kpit|coforge|genpact|virtusa|nagarro)\b', re.IGNORECASE),
    re.compile(r'\b(itc infotech|sutherland global|happiest minds|brillio|quest global|citiustech)\b', re.IGNORECASE),
    re.compile(r'\b(collabera|teamlease|quess corp|teksystems|pyramid consulting|idc technologies)\b', re.IGNORECASE),
    re.compile(r'\b(infotech|technologies limited|it consultancy|staffing solutions|manpower services)\b', re.IGNORECASE),
]

def clean_company_name(name: str) -> str:
    if not name:
        return ""
    # Normalize: lowercase, remove punctuation & corporate suffixes
    clean = name.lower().strip()
    clean = re.sub(r'[\(\)\[\],.\-\/]', ' ', clean)
    clean = re.sub(r'\b(pvt|ltd|limited|inc|corp|corporation|llc|gmbh|co|services|technologies|solutions)\b', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def is_service_company(company_name: str) -> bool:
    """
    Checks if a company is a recognized Indian IT service company, mass outsourcing firm,
    or third-party staffing agency.
    """
    if not company_name:
        return False
    
    raw_lower = company_name.lower().strip()
    normalized = clean_company_name(company_name)

    # Direct set lookup on raw lower or normalized name
    if raw_lower in INDIAN_SERVICE_COMPANIES or normalized in INDIAN_SERVICE_COMPANIES:
        return True

    # Check if normalized string matches any key in our set
    for target in INDIAN_SERVICE_COMPANIES:
        if target in raw_lower or target in normalized:
            return True

    # Regex patterns check
    for pattern in SERVICE_PATTERNS:
        if pattern.search(raw_lower):
            return True

    return False

def filter_jobs_by_company(jobs: List[Dict[str, Any]], exclude_service: bool = True) -> List[Dict[str, Any]]:
    """
    Filters out service-based companies if exclude_service is True.
    Tags each job with is_service_company for frontend badge visibility.
    """
    filtered = []
    for job in jobs:
        comp_name = job.get('company_name', '')
        is_svc = is_service_company(comp_name)
        job['is_service_company'] = is_svc
        
        if exclude_service and is_svc:
            continue
        
        filtered.append(job)
    return filtered
