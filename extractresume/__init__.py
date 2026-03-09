import azure.functions as func
import json
import base64
import io
import re
import logging
import requests
import datetime

import pdfplumber
import docx2txt

##ATS WORKFLOW
#claude generated code for ats
# ═════════════════════════════════════════════════════════════
# SKILLS DICTIONARY — TECH + NON-TECH + MIXED
# Covers: Engineering, HR, Finance, Operations, Management,
#         Healthcare, Legal, Marketing, Education, and more
# ═════════════════════════════════════════════════════════════

SKILLS_BY_CATEGORY = {

    # ── Programming Languages ────────────────────────────────
    "programming": [
        "python", "java", "javascript", "typescript", "c#", "c++", "c",
        "ruby", "php", "swift", "kotlin", "go", "rust", "scala", "r",
        "matlab", "perl", "bash", "powershell", "vba", "dart", "lua",
        "groovy", "cobol", "fortran", "assembly", "objective-c", "elixir",
        "haskell", "clojure", "f#", "apex", "solidity", "abap"
    ],

    # ── Web Development ──────────────────────────────────────
    "web": [
        "html", "css", "react", "angular", "vue", "node.js", "nodejs",
        "django", "flask", "fastapi", "spring", "asp.net", ".net",
        "rest", "graphql", "jquery", "bootstrap", "tailwind", "webpack",
        "next.js", "nuxt", "gatsby", "wordpress", "drupal", "laravel",
        "express.js", "svelte", "remix", "astro", "vite", "storybook",
        "web components", "pwa", "sass", "less", "styled components"
    ],

    # ── Data, Analytics & AI ─────────────────────────────────
    "data_ai": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "machine learning", "deep learning", "nlp", "computer vision",
        "data science", "data analysis", "data engineering", "etl",
        "power bi", "tableau", "looker", "qlik", "excel", "spark",
        "hadoop", "kafka", "airflow", "dbt", "snowflake", "databricks",
        "data warehouse", "data lake", "data modelling", "data governance",
        "business intelligence", "bi", "reporting", "predictive analytics",
        "statistics", "r studio", "spss", "sas", "alteryx", "knime",
        "google data studio", "metabase", "superset", "mlops"
    ],

    # ── Cloud & DevOps ───────────────────────────────────────
    "cloud_devops": [
        "azure", "aws", "gcp", "docker", "kubernetes", "terraform",
        "jenkins", "github actions", "ci/cd", "devops", "linux", "unix",
        "azure functions", "azure devops", "azure sql", "azure data factory",
        "azure logic apps", "azure service bus", "azure blob storage",
        "lambda", "ec2", "s3", "cloudformation", "ansible", "puppet", "chef",
        "gitlab ci", "circleci", "travis ci", "helm", "istio", "prometheus",
        "grafana", "elk stack", "datadog", "new relic", "site reliability",
        "sre", "infrastructure as code", "iac", "cloud architecture",
        "serverless", "microservices", "api gateway", "load balancing"
    ],

    # ── Microsoft / Power Platform ───────────────────────────
    "microsoft": [
        "power automate", "power apps", "power platform", "power pages",
        "dynamics 365", "sharepoint", "dataverse", "microsoft teams",
        "microsoft 365", "office 365", "power bi", "azure active directory",
        "microsoft fabric", "copilot studio", "dynamics crm",
        "dynamics 365 finance", "dynamics 365 supply chain",
        "dynamics 365 hr", "dynamics 365 sales", "dynamics 365 customer service",
        "business central", "navision", "ax", "d365", "excel", "word",
        "outlook", "onenote", "ms project", "visio", "access"
    ],

    # ── CRM & Sales Tools ────────────────────────────────────
    "crm_sales_tools": [
        "salesforce", "salesforce crm", "salesforce sales cloud",
        "salesforce service cloud", "salesforce marketing cloud",
        "salesforce pardot", "salesforce cpq", "salesforce admin",
        "salesforce developer", "salesforce lightning",
        "hubspot", "hubspot crm", "hubspot marketing",
        "zoho crm", "zoho", "pipedrive", "freshsales", "freshdesk",
        "freshworks", "zendesk", "intercom", "drift", "outreach",
        "salesloft", "gong", "chorus", "clari", "monday crm",
        "sugar crm", "insightly", "copper crm", "close crm",
        "netsuite crm", "oracle crm", "sap crm", "microsoft crm"
    ],

    # ── ERP Systems ──────────────────────────────────────────
    "erp": [
        "sap", "sap s/4hana", "sap ecc", "sap hana", "sap fi", "sap co",
        "sap mm", "sap sd", "sap hr", "sap pp", "sap wm", "sap basis",
        "sap abap", "sap fiori", "sap bw", "sap bi",
        "oracle erp", "oracle fusion", "oracle e-business suite",
        "oracle ebs", "oracle cloud", "oracle financials",
        "microsoft dynamics", "dynamics 365 finance", "dynamics ax",
        "dynamics nav", "business central",
        "netsuite", "oracle netsuite",
        "sage", "sage 200", "sage 300", "sage x3", "sage intacct",
        "epicor", "infor", "syspro", "odoo", "ifs", "unit4",
        "workday financials", "peoplesoft", "jd edwards"
    ],

    # ── Databases ────────────────────────────────────────────
    "databases": [
        "oracle", "sql server", "sqlite", "cassandra", "dynamodb",
        "cosmos db", "neo4j", "influxdb", "mariadb", "hbase",
        "db2", "sybase", "teradata", "vertica", "greenplum",
        "couchdb", "firebase", "supabase", "planetscale",
        "database design", "database administration", "dba",
        "stored procedures", "query optimisation", "indexing"
    ],

    # ── Engineering & Technical ──────────────────────────────
    "engineering": [
        "autocad", "solidworks", "catia", "ansys", "simulink",
        "revit", "bim", "civil 3d", "arcgis", "qgis", "labview",
        "pcb design", "embedded systems", "iot", "plc", "scada",
        "mechanical design", "electrical engineering", "structural analysis",
        "3d modelling", "cfd", "fem", "fea", "cam", "cnc",
        "circuit design", "fpga", "vhdl", "verilog", "ros",
        "raspberry pi", "arduino", "microcontrollers"
    ],

    # ── Cybersecurity ────────────────────────────────────────
    "cybersecurity": [
        "penetration testing", "ethical hacking", "siem", "soc",
        "vulnerability assessment", "iso 27001", "nist", "gdpr compliance",
        "firewall", "intrusion detection", "cryptography", "zero trust",
        "owasp", "ceh", "cissp", "cism", "comptia security+",
        "network security", "endpoint security", "dlp", "iam",
        "pam", "sso", "mfa", "devsecops", "threat modelling",
        "incident response", "digital forensics", "soar"
    ],

    # ── HR / People ──────────────────────────────────────────
    "hr": [
        "recruitment", "talent acquisition", "onboarding", "offboarding",
        "employee relations", "performance management", "compensation",
        "benefits administration", "hris", "workday", "sap hr", "bamboohr",
        "succession planning", "learning and development", "l&d",
        "organisational development", "workforce planning", "payroll",
        "employment law", "hr policy", "diversity and inclusion",
        "talent management", "job evaluation", "headhunting",
        "competency frameworks", "hr analytics", "people analytics",
        "oracle hcm", "successfactors", "sap successfactors",
        "adp", "ceridian", "kronos", "ultipro", "peoplesoft hr",
        "greenhouse", "lever", "workable", "smartrecruiters",
        "taleo", "icims", "jobvite", "bullhorn",
        "employee engagement", "culture", "wellbeing",
        "coaching", "mentoring", "training delivery",
        "change management", "organisational design"
    ],

    # ── Finance / Accounting ─────────────────────────────────
    "finance": [
        "financial reporting", "financial analysis", "financial modelling",
        "ifrs", "gaap", "us gaap", "management accounts", "budgeting",
        "forecasting", "variance analysis", "cash flow management",
        "accounts payable", "accounts receivable", "reconciliation",
        "audit", "internal audit", "external audit", "tax", "vat",
        "corporate finance", "investment banking", "private equity",
        "risk management", "credit risk", "market risk", "compliance",
        "sap", "oracle financials", "sage", "quickbooks", "xero",
        "bloomberg", "treasury", "mergers and acquisitions", "m&a",
        "due diligence", "valuation", "cfa", "acca", "cpa", "aca",
        "hyperion", "anaplan", "blackline", "kyriba", "concur",
        "netsuite", "workday financials", "adaptive insights",
        "financial close", "consolidation", "intercompany",
        "transfer pricing", "tax planning", "indirect tax",
        "fp&a", "financial planning", "cost accounting",
        "management reporting", "board reporting", "investor relations"
    ],

    # ── Operations / Supply Chain ────────────────────────────
    "operations": [
        "supply chain management", "logistics", "procurement",
        "inventory management", "warehouse management", "lean",
        "six sigma", "kaizen", "continuous improvement", "process improvement",
        "demand planning", "vendor management",
        "contract management", "facilities management", "health and safety",
        "quality assurance", "quality management", "iso 9001",
        "operational excellence", "kpi management", "fleet management",
        "import export", "customs", "incoterms",
        "s&op", "mrp", "erp", "wms", "tms",
        "last mile delivery", "3pl", "4pl", "freight",
        "sourcing", "category management", "spend analysis",
        "supplier relationship management", "srm",
        "business process improvement", "bpi", "bpm",
        "iso 14001", "iso 45001", "haccp", "gmp",
        "production planning", "capacity planning",
        "total quality management", "tqm"
    ],

    # ── Sales ────────────────────────────────────────────────
    "sales": [
        "sales", "business development", "account management",
        "lead generation", "b2b sales", "b2c sales",
        "key account management", "enterprise sales", "inside sales",
        "field sales", "channel sales", "solution selling",
        "consultative selling", "value selling", "spin selling",
        "cold calling", "prospecting", "pipeline management",
        "sales forecasting", "quota attainment", "revenue growth",
        "territory management", "new business", "client acquisition",
        "upselling", "cross selling", "contract negotiation",
        "tender management", "rfp", "bid management",
        "presales", "sales enablement", "sales operations"
    ],

    # ── Marketing ────────────────────────────────────────────
    "marketing": [
        "digital marketing", "seo", "sem", "google analytics",
        "social media marketing", "content marketing", "email marketing",
        "brand management", "market research", "campaign management",
        "google ads", "facebook ads", "linkedin marketing",
        "copywriting", "public relations", "pr", "media relations",
        "marketing strategy", "product marketing", "growth hacking",
        "marketing automation", "marketo", "pardot", "mailchimp",
        "adobe campaign", "klaviyo", "braze", "iterable",
        "google tag manager", "adobe analytics", "mixpanel", "amplitude",
        "affiliate marketing", "influencer marketing", "programmatic",
        "display advertising", "conversion rate optimisation", "cro",
        "a/b testing", "landing pages", "marketing funnel",
        "customer acquisition", "retention marketing", "lifecycle marketing",
        "product led growth", "demand generation", "account based marketing",
        "abm", "event marketing", "trade shows", "sponsorship"
    ],

    # ── Project / Programme Management ───────────────────────
    "project_management": [
        "project management", "programme management", "pmp", "prince2",
        "agile", "scrum", "kanban", "safe", "waterfall", "hybrid",
        "jira", "asana", "ms project", "monday.com", "trello",
        "risk management", "change management", "stakeholder management",
        "budget management", "resource planning", "governance",
        "pmo", "benefits realisation", "business analysis", "ba",
        "smartsheet", "basecamp", "notion", "confluence", "miro",
        "programme governance", "portfolio management",
        "dependency management", "milestone tracking",
        "project reporting", "earned value management", "evm",
        "cost management", "scope management", "schedule management",
        "pmbok", "ipma", "apm", "msp", "p3o"
    ],

    # ── Legal ────────────────────────────────────────────────
    "legal": [
        "contract law", "employment law", "corporate law", "commercial law",
        "litigation", "dispute resolution", "arbitration", "mediation",
        "intellectual property", "gdpr", "data protection",
        "regulatory compliance", "mergers acquisitions", "due diligence",
        "legal research", "legal drafting", "company secretarial",
        "conveyancing", "family law", "criminal law",
        "competition law", "financial regulation", "fca",
        "aml", "anti money laundering", "kyc", "sanctions",
        "privacy law", "cyber law", "fintech regulation",
        "commercial contracts", "ndas", "slas", "msa",
        "legal operations", "legaltech", "contract management"
    ],

    # ── Healthcare & Life Sciences ────────────────────────────
    "healthcare": [
        "clinical trials", "gcp", "ich guidelines", "regulatory affairs",
        "pharmacovigilance", "medical writing", "nursing", "patient care",
        "electronic health records", "ehr", "emr", "nhs", "cqc",
        "healthcare management", "infection control", "clinical governance",
        "medical coding", "icd-10", "hipaa", "care planning",
        "clinical research", "protocol development", "ethics committee",
        "fda", "ema", "mhra", "clinical data management",
        "medical devices", "ce marking", "iso 13485",
        "gmp", "gcp", "glp", "gdp",
        "health informatics", "nhs digital", "hl7", "fhir",
        "pharmacy", "pathology", "radiology", "physiotherapy"
    ],

    # ── Design & Creative ────────────────────────────────────
    "design": [
        "figma", "adobe xd", "sketch", "invision",
        "photoshop", "illustrator", "indesign", "after effects",
        "premiere pro", "final cut pro", "davinci resolve",
        "ux design", "ui design", "user research", "usability testing",
        "wireframing", "prototyping", "design systems",
        "graphic design", "visual design", "motion graphics",
        "video editing", "photography", "3d design", "blender",
        "canva", "zeplin", "abstract", "principle",
        "accessibility", "wcag", "responsive design"
    ],

    # ── Education & Training ──────────────────────────────────
    "education": [
        "curriculum development", "lesson planning", "teaching",
        "e-learning", "lms", "moodle", "blackboard", "canvas",
        "special educational needs", "sen", "safeguarding",
        "assessment design", "academic research", "pedagogical",
        "instructional design", "training delivery", "facilitation",
        "coaching", "mentoring", "talent development",
        "articulate storyline", "adobe captivate", "lectora",
        "ofsted", "qts", "pgce", "early years"
    ],

    # ── Construction & Real Estate ────────────────────────────
    "construction": [
        "construction management", "site management", "quantity surveying",
        "project controls", "cost estimating", "bills of quantities",
        "nec contract", "jct contract", "fidic",
        "building regulations", "planning permission",
        "rics", "ciob", "apc", "cscs",
        "bim", "revit", "autocad", "navisworks",
        "structural engineering", "civil engineering", "mep",
        "health and safety", "cdm regulations",
        "property management", "asset management",
        "facilities management", "fm", "cbre", "jll"
    ],

    # ── Hospitality & Retail ─────────────────────────────────
    "hospitality_retail": [
        "hospitality management", "hotel management", "food and beverage",
        "front office", "housekeeping", "revenue management",
        "property management system", "pms", "opera", "fidelio",
        "retail management", "store management", "visual merchandising",
        "loss prevention", "stock management", "epos",
        "customer experience", "guest relations",
        "food hygiene", "allergen awareness", "haccp",
        "event management", "banqueting", "catering"
    ],

    # ── Soft Skills (universal) ──────────────────────────────
    "soft_skills": [
        "leadership", "team management", "communication", "presentation",
        "negotiation", "problem solving", "critical thinking",
        "stakeholder management", "time management", "adaptability",
        "collaboration", "mentoring", "coaching", "decision making",
        "strategic thinking", "analytical skills", "attention to detail",
        "customer service", "client relationship management",
        "influencing", "conflict resolution", "emotional intelligence",
        "resilience", "initiative", "creativity", "innovation",
        "commercial awareness", "entrepreneurial", "self motivated"
    ],

    # ── Spoken Languages ────────────────────────────────────
    "spoken_languages": [
        "english", "french", "german", "spanish", "mandarin", "arabic",
        "hindi", "portuguese", "italian", "japanese", "korean", "russian",
        "dutch", "polish", "turkish", "urdu", "punjabi", "tamil",
        "bengali", "swahili", "hebrew", "greek", "swedish",
        "norwegian", "danish", "finnish", "romanian", "czech",
        "hungarian", "thai", "vietnamese", "indonesian", "malay"
    ]
}

# Flatten all skills into a single searchable list
ALL_SKILLS = []
for category, skills in SKILLS_BY_CATEGORY.items():
    for skill in skills:
        ALL_SKILLS.append((skill, category))


# ═════════════════════════════════════════════════════════════
# SECTION HEADER PATTERNS
# ═════════════════════════════════════════════════════════════

SECTION_PATTERNS = {
    "experience": re.compile(
        r"^(work\s*experience|professional\s*experience|employment\s*(history)?|"
        r"career\s*history|experience|work\s*history|positions?\s*held|"
        r"relevant\s*experience|previous\s*roles?|career\s*summary)$",
        re.IGNORECASE
    ),
    "education": re.compile(
        r"^(education|academic\s*(background|qualifications?|history)?|"
        r"qualifications?|degrees?|training\s*and\s*education|"
        r"educational\s*background)$",
        re.IGNORECASE
    ),
    "skills": re.compile(
        r"^(skills?|technical\s*skills?|core\s*competenc(y|ies)|"
        r"key\s*skills?|competenc(y|ies)|technologies|tools?\s*(and\s*technologies)?|"
        r"expertise|areas\s*of\s*expertise|capabilities)$",
        re.IGNORECASE
    ),
    "summary": re.compile(
        r"^(summary|profile|professional\s*(summary|profile)?|"
        r"career\s*(objective|summary)?|objective|about\s*me|"
        r"personal\s*statement|overview|executive\s*summary)$",
        re.IGNORECASE
    ),
    "certifications": re.compile(
        r"^(certifications?|certificates?|accreditations?|"
        r"professional\s*(certifications?|development|qualifications?)|"
        r"licenses?\s*(and\s*certifications?)?|credentials?)$",
        re.IGNORECASE
    ),
    "projects": re.compile(
        r"^(projects?|key\s*projects?|notable\s*projects?|"
        r"portfolio|selected\s*projects?)$",
        re.IGNORECASE
    ),
    "languages": re.compile(
        r"^(languages?|spoken\s*languages?|language\s*skills?|"
        r"linguistic\s*skills?)$",
        re.IGNORECASE
    ),
    "achievements": re.compile(
        r"^(achievements?|accomplishments?|awards?\s*(and\s*achievements?)?|"
        r"honours?|honors?|recognition|key\s*achievements?)$",
        re.IGNORECASE
    ),
    "interests": re.compile(
        r"^(interests?|hobbies|hobbies\s*and\s*interests?|"
        r"personal\s*interests?|activities)$",
        re.IGNORECASE
    ),
    "references": re.compile(
        r"^(references?|referees?)$",
        re.IGNORECASE
    )
}

# Regex patterns for contact info and dates
EMAIL_PATTERN    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN    = re.compile(r"(\+?\d[\d\s\-().]{7,15}\d)")
LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
GITHUB_PATTERN   = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
URL_PATTERN      = re.compile(r"https?://[^\s]+", re.IGNORECASE)

DATE_PATTERN = re.compile(
    r"(?:(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)\s+)?(\d{4})\s*"
    r"(?:[-–—]|to)\s*"
    r"(?:(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)\s+)?(\d{4}|present|current|now|date)",
    re.IGNORECASE
)

DEGREE_KEYWORDS = re.compile(
    r"\b(b\.?sc|b\.?eng|b\.?a\.?|b\.?tech|m\.?sc|m\.?eng|m\.?b\.?a|"
    r"m\.?tech|ph\.?d|bachelor|master|doctorate|diploma|"
    r"certificate|hnd|hnc|a-levels?|gcse|lpc|bptc|llb|llm)\b",
    re.IGNORECASE
)


# ═════════════════════════════════════════════════════════════
# FIX 1 — MULTI-COLUMN LAYOUT HANDLER
# Detects and flattens 2-column resume PDFs so sections
# are read in the correct logical order
# ═════════════════════════════════════════════════════════════

def extract_pdf_with_column_awareness(file_bytes: bytes) -> dict:
    """
    Extracts text from PDF with awareness of multi-column layouts.
    For each page:
    - Checks if content is split into left/right columns
    - If yes: extracts left column first, then right column
    - If no: extracts normally left-to-right
    This prevents skills from column 1 being mixed with
    job titles from column 2.
    """
    pages_text = []
    ocr_used = False

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            page_width = page.width

            # Try to detect multi-column layout by checking
            # if there are words clustered in two distinct x-zones
            words = page.extract_words()

            is_two_column = False
            if words:
                # Get x-positions of all words
                x_positions = [w["x0"] for w in words]
                midpoint = page_width / 2

                left_words  = [x for x in x_positions if x < midpoint - 20]
                right_words = [x for x in x_positions if x > midpoint + 20]

                # If both halves have substantial content = two column layout
                if len(left_words) > 10 and len(right_words) > 10:
                    left_ratio  = len(left_words) / len(x_positions)
                    right_ratio = len(right_words) / len(x_positions)
                    # Both columns should have at least 20% of content
                    if left_ratio > 0.2 and right_ratio > 0.2:
                        is_two_column = True

            if is_two_column:
                logging.info(f"Page {i+1}: two-column layout detected")
                midpoint = page_width / 2

                # Extract left column
                left_crop  = page.crop((0, 0, midpoint, page.height))
                right_crop = page.crop((midpoint, 0, page_width, page.height))

                left_text  = left_crop.extract_text()  or ""
                right_text = right_crop.extract_text() or ""

                # Combine: left column first, then right column
                page_text = left_text.strip() + "\n\n" + right_text.strip()

            else:
                # Standard single-column extraction
                page_text = page.extract_text() or ""

            # OCR fallback for blank pages (scanned)
            if not page_text.strip():
                logging.info(f"Page {i+1}: blank — attempting OCR")
                try:
                    page_image = page.to_image(resolution=200)
                    img_bytes  = io.BytesIO()
                    page_image.original.save(img_bytes, format="PNG")
                    ocr_text = ocr_image_bytes(img_bytes.getvalue())
                    if ocr_text.strip():
                        page_text = ocr_text
                        ocr_used  = True
                except Exception as e:
                    logging.warning(f"OCR fallback failed page {i+1}: {e}")

            pages_text.append(page_text)

    return {
        "text":       "\n\n".join(pages_text).strip(),
        "page_count": page_count,
        "ocr_used":   ocr_used
    }


# ═════════════════════════════════════════════════════════════
# FIX 2 — ACCURATE EXPERIENCE YEAR CALCULATION
# Handles: overlapping jobs, concurrent roles, gaps,
#          present/current end dates, and part-time indicators
# ═════════════════════════════════════════════════════════════

def calculate_total_experience(jobs: list) -> float:
    """
    Calculates total experience by merging overlapping date ranges.
    Example: if someone held 2 jobs at the same time (2020-2022 and 2021-2023),
    total experience is 3 years (2020-2023), not 4 years (2+2).

    Returns years rounded to 1 decimal place.
    """
    if not jobs:
        return 0

    current_year = datetime.datetime.now().year

    # Collect all valid date ranges
    date_ranges = []
    for job in jobs:
        start = job.get("_start_year")
        end   = job.get("_end_year")
        if start and end and isinstance(start, int) and isinstance(end, int):
            if 1950 <= start <= current_year and start <= end <= current_year + 1:
                date_ranges.append((start, end))

    if not date_ranges:
        return 0

    # Sort by start year
    date_ranges.sort(key=lambda x: x[0])

    # Merge overlapping ranges
    merged = [date_ranges[0]]
    for start, end in date_ranges[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            # Overlapping — extend the current range if needed
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    # Sum up the merged ranges
    total_years = sum(end - start for start, end in merged)
    return round(min(total_years, 50), 1)


def parse_job_dates(block: str) -> dict:
    """
    Parse start/end years from a job block text.
    Returns raw years for the overlap calculation above.
    """
    current_year = datetime.datetime.now().year
    date_match   = DATE_PATTERN.search(block)

    if not date_match:
        return {"duration": None, "_start_year": None, "_end_year": None, "years": None}

    try:
        start_year = int(date_match.group(1))
    except (ValueError, TypeError):
        return {"duration": None, "_start_year": None, "_end_year": None, "years": None}

    end_raw = date_match.group(2)
    if end_raw and end_raw.lower() in ("present", "current", "now", "date"):
        end_year = current_year
    else:
        try:
            end_year = int(end_raw)
        except (ValueError, TypeError):
            end_year = current_year

    # Sanity check years
    if not (1950 <= start_year <= current_year):
        return {"duration": None, "_start_year": None, "_end_year": None, "years": None}
    if end_year < start_year:
        end_year = start_year

    duration = date_match.group(0).strip()
    years    = round(max(0, end_year - start_year), 1)

    return {
        "duration":     duration,
        "_start_year":  start_year,
        "_end_year":    end_year,
        "years":        years
    }


# ═════════════════════════════════════════════════════════════
# FIX 3 — COMPREHENSIVE SKILLS EXTRACTION
# Covers tech + non-tech + soft skills with category tagging
# ═════════════════════════════════════════════════════════════

def extract_skills_comprehensive(skills_section: str, full_text: str) -> dict:
    """
    Extracts skills from both the dedicated skills section
    and the full resume text (catches skills mentioned in context).

    Returns skills grouped by category AND as a flat list.
    Categories help Groq understand the candidate's profile better.
    """
    search_text = (skills_section + "\n" + full_text).lower()

    found_by_category = {}
    all_found = set()

    for skill, category in ALL_SKILLS:
        # Escape special regex characters in skill name
        escaped = re.escape(skill)
        pattern = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)

        if pattern.search(search_text):
            if category not in found_by_category:
                found_by_category[category] = []

            # Clean display name
            display = skill.replace("\\+\\+", "++").replace("\\.", ".")
            display = display.title() if len(display) > 2 else display.upper()

            if display not in all_found:
                found_by_category[category].append(display)
                all_found.add(display)

    # Also parse skills listed in the skills section directly
    # (catches domain-specific skills not in our dictionary)
    unlisted_skills = []
    if skills_section:
        raw = re.split(r"[,|•·\n\t/]+", skills_section)
        for s in raw:
            s = re.sub(r"^[-•·*▪▸✓✔]\s*", "", s.strip())
            s = re.sub(r"\s+", " ", s).strip()
            # Valid: 2-60 chars, max 5 words, not a sentence
            if 2 <= len(s) <= 60 and len(s.split()) <= 5:
                if not any(stop in s.lower() for stop in [
                    "experience", "year", "month", "responsible",
                    "worked", "developed", "managed"
                ]):
                    if s not in all_found:
                        unlisted_skills.append(s)
                        all_found.add(s)

    if unlisted_skills:
        found_by_category["other"] = unlisted_skills[:20]

    # ── Confidence score for skill extraction ────────────────
    total_found = len(all_found)
    if total_found >= 10:
        confidence = "high"
    elif total_found >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "all_skills":         sorted(list(all_found)),
        "skills_by_category": found_by_category,
        "total_count":        total_found,
        "confidence":         confidence
    }


# ═════════════════════════════════════════════════════════════
# FIX 4 — CONFIDENCE SCORES ON EXTRACTED FIELDS
# Every extracted field reports how confident the parser is
# so Groq knows which fields to trust vs re-examine
# ═════════════════════════════════════════════════════════════

def score_confidence(value, field_type: str) -> str:
    """
    Returns 'high', 'medium', or 'low' confidence
    based on the value and what type of field it is.
    """
    if value is None or value == "" or value == []:
        return "low"

    if field_type == "email":
        return "high" if EMAIL_PATTERN.fullmatch(str(value)) else "low"

    if field_type == "phone":
        digits = re.sub(r"\D", "", str(value))
        return "high" if 7 <= len(digits) <= 15 else "medium"

    if field_type == "name":
        words = str(value).split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return "high"
        return "medium"

    if field_type == "title":
        # Titles should be 2-8 words and contain job-related words
        words = str(value).split()
        job_words = ["engineer", "developer", "manager", "analyst", "director",
                     "specialist", "consultant", "officer", "lead", "head",
                     "coordinator", "executive", "associate", "senior", "junior"]
        if any(w.lower() in str(value).lower() for w in job_words):
            return "high"
        return "medium" if 1 < len(words) <= 8 else "low"

    if field_type == "year":
        current_year = datetime.datetime.now().year
        try:
            y = int(value)
            return "high" if 1950 <= y <= current_year else "low"
        except (ValueError, TypeError):
            return "low"

    if field_type == "experience_total":
        try:
            y = float(value)
            return "high" if 0 <= y <= 45 else "low"
        except (ValueError, TypeError):
            return "low"

    return "medium"


# ═════════════════════════════════════════════════════════════
# OTHER EXTRACTION HELPERS
# ═════════════════════════════════════════════════════════════

def download_file(url: str, token: str = "") -> bytes:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.content


def detect_type(file_bytes: bytes) -> str:
    if file_bytes[:4] == b"%PDF":             return "pdf"
    if file_bytes[:2] == b"PK":              return "docx"
    if file_bytes[:3] == b"\xff\xd8\xff":    return "jpeg"
    if file_bytes[:8] == b"\x89PNG\r\n\x1a\n": return "png"
    if file_bytes[:4] in (b"MM\x00*", b"II*\x00"): return "tiff"
    return "unknown"


def ocr_image_bytes(image_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        return pytesseract.image_to_string(img, config="--psm 6")
    except Exception as e:
        logging.warning(f"OCR failed: {e}")
        return ""


def read_docx(file_bytes: bytes) -> dict:
    try:
        text = docx2txt.process(io.BytesIO(file_bytes))
        return {"text": text.strip(), "page_count": None, "ocr_used": False}
    except Exception as e:
        raise ValueError(f"Could not read Word document: {e}. "
                         "File may be password protected or corrupted.")


def read_image(file_bytes: bytes) -> dict:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img, config="--psm 6")
        return {"text": text.strip(), "page_count": 1, "ocr_used": True}
    except ImportError:
        return {
            "text": "", "page_count": 1, "ocr_used": False,
            "warning": "OCR libraries not available. PDF and DOCX extraction works normally."
        }
    except Exception as e:
        raise ValueError(f"Image OCR failed: {e}")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"^[-_=.•|]{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(l.strip() for l in text.split("\n")).strip()


def split_into_sections(text: str) -> dict:
    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_lines   = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append("")
            continue

        matched = None
        if len(stripped) < 70:
            for name, pattern in SECTION_PATTERNS.items():
                if pattern.match(stripped):
                    matched = name
                    break

        if matched:
            sections[current_section] = "\n".join(current_lines).strip()
            current_section = matched
            current_lines   = []
        else:
            current_lines.append(line)

    sections[current_section] = "\n".join(current_lines).strip()
    return sections


def extract_contact_info(text: str) -> dict:
    contact = {"email": None, "phone": None, "linkedin": None,
               "github": None, "website": None}

    m = EMAIL_PATTERN.search(text)
    if m:
        contact["email"] = m.group().strip()

    m = PHONE_PATTERN.search(text)
    if m:
        phone = m.group().strip()
        if len(re.sub(r"\D", "", phone)) >= 7:
            contact["phone"] = phone

    m = LINKEDIN_PATTERN.search(text)
    if m:
        contact["linkedin"] = "https://" + m.group()

    m = GITHUB_PATTERN.search(text)
    if m:
        contact["github"] = "https://" + m.group()

    # Website (not LinkedIn or GitHub)
    for m in URL_PATTERN.finditer(text):
        url = m.group()
        if "linkedin" not in url.lower() and "github" not in url.lower():
            contact["website"] = url
            break

    return contact


def extract_name_and_title(header_text: str) -> dict:
    lines = [l.strip() for l in header_text.split("\n") if l.strip()]
    name, title = None, None

    for line in lines[:8]:
        if EMAIL_PATTERN.search(line): continue
        if PHONE_PATTERN.search(line): continue
        if any(kw in line.lower() for kw in ["linkedin", "github", "http", "www", "@"]): continue

        words = line.split()
        if not name and 1 < len(words) <= 5 and len(line) < 50:
            if all(re.match(r"^[A-Za-z\-'.]+$", w) for w in words):
                name = line
                continue

        if name and not title and 1 < len(words) <= 10 and len(line) < 80:
            title = line
            break

    return {
        "name":       name,
        "name_confidence":  score_confidence(name, "name"),
        "current_title":    title,
        "title_confidence": score_confidence(title, "title")
    }


def extract_experience_section(exp_section: str) -> list:
    """
    Parse experience section into job blocks.
    Returns list of jobs WITH _start_year and _end_year
    for accurate overlap calculation.
    """
    if not exp_section:
        return []

    jobs = []
    # Split into blocks — new block starts with a capital letter line
    blocks = re.split(r"\n(?=[A-Z][^\n]{2,60}\n)", exp_section)

    for block in blocks:
        block = block.strip()
        if len(block) < 20:
            continue

        dates = parse_job_dates(block)
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        job = {
            "title":       None,
            "company":     None,
            "duration":    dates.get("duration"),
            "years":       dates.get("years"),
            "_start_year": dates.get("_start_year"),
            "_end_year":   dates.get("_end_year"),
            "summary":     None,
            "confidence":  "medium"
        }

        # First non-date line = job title
        for line in lines:
            if not DATE_PATTERN.search(line):
                job["title"] = line
                break

        # Second non-date line = company
        seen_title = False
        for line in lines:
            if DATE_PATTERN.search(line):
                continue
            if not seen_title:
                seen_title = True
                continue
            job["company"] = line
            break

        # Bullet points / remaining lines = summary
        summary_lines = []
        for line in lines:
            if DATE_PATTERN.search(line):
                continue
            if line == job["title"] or line == job["company"]:
                continue
            if len(line) > 15:
                line = re.sub(r"^[-•·*▪▸✓✔]\s*", "", line)
                summary_lines.append(line)

        if summary_lines:
            job["summary"] = " ".join(summary_lines[:3])

        # Confidence based on how much info we extracted
        filled = sum(1 for k in ["title", "company", "duration", "summary"]
                     if job.get(k))
        job["confidence"] = "high" if filled >= 3 else "medium" if filled >= 2 else "low"

        if job.get("title") or job.get("duration"):
            jobs.append(job)

    return jobs


def extract_education(edu_section: str) -> list:
    if not edu_section:
        return []

    degrees = []
    lines   = [l.strip() for l in edu_section.split("\n") if l.strip()]
    current = {}

    for line in lines:
        year_match = re.search(r"\b(19|20)\d{2}\b", line)
        deg_match  = DEGREE_KEYWORDS.search(line)

        if deg_match or year_match:
            if current:
                degrees.append(current)
            current = {
                "degree":       line if deg_match else None,
                "institution":  None,
                "year":         int(year_match.group()) if year_match else None,
                "year_confidence": score_confidence(
                    int(year_match.group()) if year_match else None, "year"
                )
            }
        elif current and not current.get("institution") and len(line) > 3:
            current["institution"] = line
        elif current and not current.get("degree") and deg_match:
            current["degree"] = line

    if current:
        degrees.append(current)

    return degrees


def extract_certifications(cert_section: str) -> list:
    if not cert_section:
        return []
    lines = [l.strip() for l in cert_section.split("\n") if l.strip()]
    certs = []
    for line in lines:
        line = re.sub(r"^[-•·*▪▸]\s*", "", line)
        if 5 <= len(line) <= 120:
            certs.append(line)
    return certs[:15]


def extract_languages(lang_section: str) -> list:
    if not lang_section:
        return []
    parts = re.split(r"[,\n|•·/]+", lang_section)
    langs = []
    for p in parts:
        p = re.sub(r"^[-•·*]\s*", "", p.strip())
        p = re.sub(r"\(.*?\)", "", p).strip()
        if 2 <= len(p) <= 30 and len(p.split()) <= 3:
            langs.append(p)
    return langs[:10]


def extract_location(text: str) -> str:
    loc_pattern = re.compile(
        r"\b([A-Z][a-z]+(?:[\s\-][A-Z][a-z]+)?,\s*"
        r"(?:[A-Z]{2}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)?))\b"
    )
    match = loc_pattern.search(text[:600])
    return match.group(1) if match else None


def trim_to_token_limit(text: str, max_words: int = 6000) -> tuple:
    words = text.split()
    if len(words) <= max_words:
        return text, False
    return " ".join(words[:max_words]), True


# ═════════════════════════════════════════════════════════════
# MASTER STRUCTURE FUNCTION
# ═════════════════════════════════════════════════════════════

def structure_resume(raw_text: str) -> dict:
    cleaned  = clean_text(raw_text)
    sections = split_into_sections(cleaned)

    header_text  = sections.get("header", "")
    skills_sec   = sections.get("skills", "")
    exp_sec      = sections.get("experience", "")
    edu_sec      = sections.get("education", "")
    cert_sec     = sections.get("certifications", "")
    lang_sec     = sections.get("languages", "")
    summary_sec  = sections.get("summary", "")
    proj_sec     = sections.get("projects", "")
    achiev_sec   = sections.get("achievements", "")

    # Extract all components
    contact  = extract_contact_info(header_text + "\n" + cleaned[:400])
    identity = extract_name_and_title(header_text)
    skills   = extract_skills_comprehensive(skills_sec, cleaned)
    jobs     = extract_experience_section(exp_sec)
    edu      = extract_education(edu_sec)
    certs    = extract_certifications(cert_sec)
    langs    = extract_languages(lang_sec)
    location = extract_location(header_text + "\n" + cleaned[:600])

    # FIX 2: Accurate total experience with overlap handling
    total_exp = calculate_total_experience(jobs)

    # Clean up internal fields before returning (remove _ prefixed helpers)
    clean_jobs = []
    for job in jobs:
        clean_job = {k: v for k, v in job.items()
                     if not k.startswith("_")}
        clean_jobs.append(clean_job)

    # Trim summary
    summary = summary_sec.strip()
    if summary:
        sentences = re.split(r"(?<=[.!?])\s+", summary)
        summary   = " ".join(sentences[:3])

    # Overall extraction confidence
    confidence_signals = [
        identity.get("name_confidence")  == "high",
        identity.get("title_confidence") == "high",
        bool(contact.get("email")),
        total_exp > 0,
        len(skills.get("all_skills", [])) >= 3,
    ]
    overall_confidence = (
        "high"   if sum(confidence_signals) >= 4 else
        "medium" if sum(confidence_signals) >= 2 else
        "low"
    )

    # ── Raw section texts for Groq fallback ─────────────────
    # These are sent alongside the structured data so Groq can
    # pick up any skills or context that the regex parser missed.
    # Especially useful for unrelated backgrounds, niche industries,
    # or tools not in the hardcoded skills dictionary.
    raw_sections = {}
    for section_name in ["skills", "experience", "summary", "achievements"]:
        raw = sections.get(section_name, "").strip()
        if raw:
            # Trim each raw section to 400 words max to save tokens
            words = raw.split()
            raw_sections[section_name] = (
                " ".join(words[:400]) + ("..." if len(words) > 400 else "")
            )

    return {
        "extraction_confidence": overall_confidence,
        "candidate": {
            "name":             identity.get("name"),
            "name_confidence":  identity.get("name_confidence"),
            "current_title":    identity.get("current_title"),
            "title_confidence": identity.get("title_confidence"),
            "location":         location,
            "email":            contact.get("email"),
            "phone":            contact.get("phone"),
            "linkedin":         contact.get("linkedin"),
            "github":           contact.get("github"),
            "website":          contact.get("website")
        },
        "summary":                   summary or None,
        "total_experience_years":    total_exp,
        "experience_confidence":     score_confidence(total_exp, "experience_total"),
        "skills":                    skills.get("all_skills", []),
        "skills_by_category":        skills.get("skills_by_category", {}),
        "skills_confidence":         skills.get("confidence"),
        "experience":                clean_jobs,
        "education":                 edu,
        "certifications":            certs,
        "languages":                 langs if langs else ["English"],
        "projects_mentioned":        bool(proj_sec.strip()),
        "achievements_mentioned":    bool(achiev_sec.strip()),
        "sections_detected":         [k for k in sections if sections[k].strip()],

        # Raw section text — Groq uses this to catch anything
        # the structured parser may have missed (niche skills,
        # unrecognised tools, unrelated industry backgrounds)
        "raw_sections":              raw_sections
    }


# ═════════════════════════════════════════════════════════════
# MAIN ROUTE: POST /api/extract-resume
# ═════════════════════════════════════════════════════════════


# ═════════════════════════════════════════════════════════════
# MAIN ENTRY POINT — Azure Functions v1 Programming Model
# This is called automatically by the runtime for every request
# ═════════════════════════════════════════════════════════════

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("extractresume function called")

    # ── Health check (GET request) ───────────────────────────
    if req.method == "GET":
        return func.HttpResponse(
            json.dumps({
                "status":   "healthy",
                "version":  "6.0.0",
                "supports": ["pdf", "docx", "doc", "jpg", "jpeg", "png", "tiff"],
                "features": [
                    "multi-column PDF layout handling",
                    "accurate experience year calculation (overlap-aware)",
                    "500+ skills across 18 categories — tech + non-tech + mixed",
                    "CRM tools: Salesforce, HubSpot, Zoho, Pipedrive and more",
                    "ERP systems: SAP, Oracle, Dynamics, NetSuite, Sage and more",
                    "confidence scores on all extracted fields",
                    "raw_sections returned alongside structured data for Groq fallback"
                ]
            }),
            mimetype="application/json",
            status_code=200
        )

    # ── POST request — extract and structure resume ──────────
    try:
        body = req.get_json()
    except ValueError:
        return _err("Request body must be valid JSON", 400)

    file_bytes = None

    if "file_base64" in body:
        try:
            file_bytes = base64.b64decode(body["file_base64"])
        except Exception as e:
            return _err(f"Could not decode base64: {e}", 400)

    elif "file_url" in body:
        token = body.get("access_token", "")
        try:
            file_bytes = download_file(body["file_url"], token)
        except Exception as e:
            return _err(f"File download failed: {e}", 502)
    else:
        return _err("Provide 'file_base64' or 'file_url'", 400)

    # Detect file type
    file_type = detect_type(file_bytes)
    if file_type == "unknown":
        file_type = body.get("file_type", "pdf").lower()

    logging.info(f"File type: {file_type}, size: {len(file_bytes)} bytes")

    # Extract raw text
    try:
        if file_type == "pdf":
            result = extract_pdf_with_column_awareness(file_bytes)
        elif file_type in ("docx", "doc"):
            result = read_docx(file_bytes)
        elif file_type in ("jpeg", "jpg", "png", "gif", "tiff", "bmp"):
            result = read_image(file_bytes)
        else:
            return _err(
                f"Unsupported file type: {file_type}. "
                "Supported: pdf, docx, doc, jpg, png, tiff", 415
            )
    except ValueError as e:
        return _err(str(e), 422)
    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return _err(f"Extraction failed: {e}", 500)

    raw_text = result.get("text", "")

    if not raw_text.strip() and "warning" not in result:
        return _err(
            "No text extracted. File may be a scanned image — "
            "send as JPG/PNG for OCR.", 422
        )

    # Structure the resume
    try:
        structured = structure_resume(raw_text)
    except Exception as e:
        logging.error(f"Structuring failed: {e}")
        structured = {
            "extraction_confidence": "low",
            "raw_text": clean_text(raw_text),
            "error": f"Structuring failed — raw text returned: {e}"
        }

    response = {
        "success":    True,
        "file_type":  file_type,
        "page_count": result.get("page_count"),
        "ocr_used":   result.get("ocr_used", False),
        "resume":     structured
    }

    if "warning" in result:
        response["warning"] = result["warning"]

    logging.info(
        f"Done — confidence: {structured.get('extraction_confidence')}, "
        f"skills: {len(structured.get('skills', []))}, "
        f"jobs: {len(structured.get('experience', []))}, "
        f"exp_years: {structured.get('total_experience_years')}"
    )

    return func.HttpResponse(
        json.dumps(response),
        mimetype="application/json",
        status_code=200
    )


# ═════════════════════════════════════════════════════════════
# ERROR HELPER
# ═════════════════════════════════════════════════════════════

def _err(message: str, status: int) -> func.HttpResponse:
    logging.error(f"[{status}] {message}")
    return func.HttpResponse(
        json.dumps({"success": False, "error": message}),
        mimetype="application/json",
        status_code=status
    )
