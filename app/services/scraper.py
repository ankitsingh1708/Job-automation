import re
import asyncio
import urllib.parse
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from app.services.cache import cache
from app.services.mock_data import generate_mock_jobs
from app.services.company_filter import filter_jobs_by_company, is_service_company
from app.services.salary_engine import resolve_job_salary, extract_salary_from_text

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
]

BASE_SEARCH_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
TIME_POSTED_MAP = {
    '24h': 'r86400',
    'day': 'r86400',
    'r86400': 'r86400',
    'past_24h': 'r86400',
    'past 24 hours': 'r86400',
    'week': 'r604800',
    'r604800': 'r604800',
    'past_week': 'r604800',
    'past week': 'r604800',
    'month': 'r2592000',
    'r2592000': 'r2592000',
    'past_month': 'r2592000',
    'past month': 'r2592000'
}

WORKPLACE_TYPE_MAP = {
    'on-site': '1',
    'remote': '2',
    'hybrid': '3'
}

JOB_TYPE_MAP = {
    'full-time': 'F',
    'part-time': 'P',
    'contract': 'C',
    'temporary': 'T',
    'internship': 'I'
}

EXPERIENCE_LEVEL_MAP = {
    'internship': '1',
    'entry': '2',
    'associate': '3',
    'mid-senior': '4',
    'director': '5',
    'executive': '6'
}

def extract_experience_required(description: str = '', title: str = '') -> str:
    full = (title + ' ' + (description or '')).strip()
    if not full:
        return '1–3 Years'
        
    if re.search(r'\b(fresher|entry level|graduate trainee|0\s*-\s*1\s*years?|no experience|intern|internship)\b', full, re.I):
        return '0–1 Years (Fresher)'
        
    # Range like '3-5 years', '3 to 5 years', '3 - 6 yrs'
    m_range = re.search(r'(\d{1,2})\s*(?:-|to|–)\s*(\d{1,2})\s*(?:\+)?\s*(?:years?|yrs?)(?:\s*(?:of)?\s*(?:relevant|hands-on|industry|software)?\s*experience)?', full, re.I)
    if m_range:
        return f"{m_range.group(1)}–{m_range.group(2)} Years"
        
    # Minimum like '5+ years', 'minimum 3 years', 'at least 4 years'
    m_min = re.search(r'(?:min(?:imum)?|at least|\+)?\s*(\d{1,2})\s*\+\s*(?:years?|yrs?)(?:\s*(?:of)?\s*(?:experience)?)?', full, re.I)
    if m_min:
        return f"{m_min.group(1)}+ Years"
        
    m_min2 = re.search(r'(?:min(?:imum)?|at least)\s*(\d{1,2})\s*(?:years?|yrs?)', full, re.I)
    if m_min2:
        return f"{m_min2.group(1)}+ Years"
        
    m_gen = re.search(r'(\d{1,2})\s*(?:years?|yrs?)(?:\s*(?:of)?\s*(?:relevant|hands-on|industry)?\s*experience)', full, re.I)
    if m_gen:
        return f"{m_gen.group(1)}+ Years"

    # Title-based fallback calibration
    t_lower = title.lower()
    if any(w in t_lower for w in ['principal', 'staff', 'architect', 'director', 'vp', 'head']):
        return '8–12+ Years'
    elif any(w in t_lower for w in ['lead', 'tech lead', 'manager', 'iv', '4']):
        return '6–9 Years'
    elif any(w in t_lower for w in ['senior', 'sr', 'iii', '3', 'expert']):
        return '4–7 Years'
    elif any(w in t_lower for w in ['ii', '2', 'mid', 'middle']):
        return '2–5 Years'
    elif any(w in t_lower for w in ['junior', 'jr', 'entry', 'associate', 'i', '1', 'intern', 'trainee']):
        return '0–2 Years'
        
    return '2–4 Years'

async def fetch_single_batch(client: httpx.AsyncClient, params: Dict[str, Any], headers: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        resp = await client.get(BASE_SEARCH_URL, params=params, headers=headers)
        if resp.status_code == 200 and resp.text.strip():
            return parse_job_cards(resp.text)
    except Exception:
        pass
    return []

async def search_linkedin_jobs(
    keywords: str = '',
    location: str = '',
    remote: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    date_posted: Optional[str] = None,
    exclude_service_companies: bool = False,
    page: int = 1,
    limit: int = 40
) -> Dict[str, Any]:
    """
    Searches LinkedIn for jobs matching criteria using concurrent multi-batch fetching.
    """
    cache_key = f"jobs_search_v3:{keywords}:{location}:{remote}:{job_type}:{experience_level}:{date_posted}:{exclude_service_companies}:{page}:{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Calculate starting offset (each page covers 30-40 jobs)
    base_start = (page - 1) * 30
    offsets = [base_start, base_start + 10, base_start + 20, base_start + 30]

    base_params: Dict[str, Any] = {
        'keywords': keywords,
        'location': location or 'Worldwide',
    }

    if date_posted and date_posted.lower() in TIME_POSTED_MAP:
        base_params['f_TPR'] = TIME_POSTED_MAP[date_posted.lower()]

    if remote and remote.lower() in WORKPLACE_TYPE_MAP:
        base_params['f_WT'] = WORKPLACE_TYPE_MAP[remote.lower()]

    if job_type and job_type.lower() in JOB_TYPE_MAP:
        base_params['f_JT'] = JOB_TYPE_MAP[job_type.lower()]

    if experience_level and experience_level.lower() in EXPERIENCE_LEVEL_MAP:
        base_params['f_E'] = EXPERIENCE_LEVEL_MAP[experience_level.lower()]

    headers = {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.linkedin.com/jobs',
        'sec-ch-ua': '"Chromium";v="123", "Not:A-Brand";v="8"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
    }

    all_jobs: List[Dict[str, Any]] = []
    seen_ids = set()
    source = 'live'
    error_message = None

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = []
            for offset in offsets:
                p = dict(base_params)
                p['start'] = offset
                tasks.append(fetch_single_batch(client, p, headers))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for batch in results:
                if isinstance(batch, list):
                    for job in batch:
                        if job['id'] not in seen_ids:
                            seen_ids.add(job['id'])
                            all_jobs.append(job)
    except Exception as e:
        error_message = f"Error requesting LinkedIn: {str(e)}"

    # If live search yielded nothing, use fallback mock generator
    if not all_jobs:
        source = 'fallback'
        all_jobs = generate_mock_jobs(keywords=keywords, location=location, limit=30)

    # Filter out service-based companies if requested, and tag all jobs
    all_jobs = filter_jobs_by_company(all_jobs, exclude_service=exclude_service_companies)

    result = {
        'source': source,
        'page': page,
        'limit': limit,
        'total_count': len(all_jobs),
        'keywords': keywords,
        'location': location,
        'exclude_service_companies': exclude_service_companies,
        'error_note': error_message if source == 'fallback' else None,
        'jobs': all_jobs
    }

    cache.set(cache_key, result, ttl=300)
    return result

def parse_job_cards(html_content: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    job_cards = soup.find_all(['li', 'div'], class_=re.compile(r'(base-card|job-search-card)'))
    parsed_jobs = []

    for card in job_cards:
        try:
            # Job Title & Link
            title_elem = card.find(['h3', 'a'], class_=re.compile(r'(base-search-card__title|job-search-card__title)'))
            if not title_elem:
                title_elem = card.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else 'Job Title'

            link_elem = card.find('a', class_=re.compile(r'(base-card__full-link|job-search-card__url-link)'))
            job_url = link_elem['href'] if link_elem and link_elem.has_attr('href') else ''
            
            if job_url:
                job_url = job_url.split('?')[0]

            # Extract job ID
            job_id_match = re.search(r'view/(\d+)', job_url) or re.search(r'currentJobId=(\d+)', job_url) or re.search(r'-(\d+)$', job_url)
            job_id = job_id_match.group(1) if job_id_match else f"urn-{abs(hash(title + job_url)) % 10000000}"

            # Company Name & Link
            company_elem = card.find(['h4', 'a'], class_=re.compile(r'(base-search-card__subtitle|job-search-card__subtitle)'))
            company_name = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'

            # Company Logo
            logo_elem = card.find('img', class_=re.compile(r'(artdeco-entity-image|job-search-card__logo-image)'))
            logo_url = ''
            if logo_elem:
                logo_url = logo_elem.get('data-delayed-url') or logo_elem.get('src') or ''
            
            if not logo_url or 'data:image' in logo_url:
                clean_comp = re.sub(r'[^a-zA-Z0-9]', '', company_name).lower()
                logo_url = f"https://logo.clearbit.com/{clean_comp}.com"

            # Location
            loc_elem = card.find(['span', 'div'], class_=re.compile(r'(job-search-card__location|job-search-card__location-text)'))
            location = loc_elem.get_text(strip=True) if loc_elem else 'Location not specified'

            # Listed Date / Time
            time_elem = card.find('time')
            posted_time = time_elem.get_text(strip=True) if time_elem else 'Recently'

            # Salary Snippet
            salary_elem = card.find(['span', 'div'], class_=re.compile(r'job-search-card__salary-info'))
            salary = salary_elem.get_text(strip=True) if salary_elem else None

            # Salary Resolution (Direct Scrape, LeetCode Verified, or Market Estimate)
            salary_data = resolve_job_salary(
                raw_salary=salary,
                title=title,
                company_name=company_name,
                location=location,
                experience_level='Mid-Senior level'
            )

            # Badges / Urgency
            is_easy_apply = bool(card.find(string=re.compile(r'Easy Apply', re.IGNORECASE)))
            is_urgent = bool(card.find(string=re.compile(r'Actively recruiting|Urgent|Be an early applicant', re.IGNORECASE)))

            # Workplace Type determination
            workplace_type = 'On-site'
            loc_lower = location.lower()
            title_lower = title.lower()
            if 'remote' in loc_lower or 'remote' in title_lower:
                workplace_type = 'Remote'
            elif 'hybrid' in loc_lower or 'hybrid' in title_lower:
                workplace_type = 'Hybrid'

            # Experience Required Extraction
            exp_req = extract_experience_required(title=title)

            parsed_jobs.append({
                'id': str(job_id),
                'title': title,
                'company_name': company_name,
                'company_logo': logo_url,
                'company_rating': 4.3,
                'company_size': 'Corporate',
                'location': location,
                'workplace_type': workplace_type,
                'job_type': 'Full-time',
                'experience_level': 'Mid-Senior level',
                'experience_required': exp_req,
                'salary': salary_data['salary'],
                'salary_type': salary_data['salary_type'],
                'is_salary_estimated': salary_data.get('is_estimated', False),
                'posted_time': posted_time,
                'description': f"Explore this opening for {title} at {company_name}. Click 'Apply on LinkedIn' to view full qualification criteria and submit your application.",
                'skills': [s.strip() for s in title.split() if len(s) > 3][:4] + ['Teamwork', 'Communication'],
                'is_urgent': is_urgent,
                'is_easy_apply': is_easy_apply,
                'linkedin_url': job_url or f"https://www.linkedin.com/jobs/view/{job_id}",
                'is_fallback': False
            })
        except Exception:
            continue

    return parsed_jobs

async def get_job_details(job_id: str) -> Dict[str, Any]:
    """
    Fetches full job description and criteria by job ID from LinkedIn guest endpoint.
    """
    cache_key = f"job_details:{job_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    url = f"{BASE_JOB_URL}/{job_id}"
    headers = {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200 and resp.text.strip():
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Title
                title_elem = soup.find(['h2', 'h1'], class_=re.compile(r'top-card-layout__title|topcard__title'))
                title = title_elem.get_text(strip=True) if title_elem else 'Job Title'

                # Company
                comp_elem = soup.find(['a', 'span'], class_=re.compile(r'topcard__org-name-link|topcard__flavor'))
                company_name = comp_elem.get_text(strip=True) if comp_elem else 'Company'

                # Description
                desc_elem = soup.find('div', class_=re.compile(r'show-more-less-html__markup|description__text'))
                description_html = str(desc_elem) if desc_elem else '<p>No detailed description provided.</p>'
                description_text = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ''

                # Resolve Salary with full description text & company tier
                salary_data = resolve_job_salary(
                    title=title,
                    company_name=company_name,
                    description_text=description_text
                )

                # Extract Experience Required from full description & title
                exp_req = extract_experience_required(description=description_text, title=title)

                # Criteria list
                criteria = {}
                for item in soup.find_all('li', class_=re.compile(r'description__job-criteria-item')):
                    sub_header = item.find('h3')
                    val = item.find('span')
                    if sub_header and val:
                        criteria[sub_header.get_text(strip=True)] = val.get_text(strip=True)

                details = {
                    'id': str(job_id),
                    'title': title,
                    'company_name': company_name,
                    'salary': salary_data['salary'],
                    'salary_type': salary_data['salary_type'],
                    'is_salary_estimated': salary_data.get('is_estimated', False),
                    'experience_required': exp_req,
                    'description_html': description_html,
                    'description_text': description_text,
                    'criteria': criteria,
                    'apply_url': f"https://www.linkedin.com/jobs/view/{job_id}",
                    'is_live': True
                }
                cache.set(cache_key, details, ttl=600)
                return details
    except Exception:
        pass

    # Fallback details if not found or rate-limited
    mock_jobs = generate_mock_jobs(limit=30)
    matching = next((j for j in mock_jobs if str(j['id']) == str(job_id)), mock_jobs[0])
    details = {
        'id': str(job_id),
        'title': matching['title'],
        'company_name': matching['company_name'],
        'description_html': f"<div><p>{matching['description'].replace(chr(10), '<br>')}</p></div>",
        'description_text': matching['description'],
        'criteria': {
            'Seniority level': matching['experience_level'],
            'Employment type': matching['job_type'],
            'Job function': 'Engineering / Technology',
            'Industries': 'Technology, Software & Internet'
        },
        'apply_url': matching['linkedin_url'],
        'is_live': False
    }
    return details
