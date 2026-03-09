# ATS Resume Extractor — Azure Function

## Overview
HTTP-triggered Azure Function that extracts and structures resume data
from PDF, DOCX, DOC, JPG, and PNG files for ATS scoring via Groq AI.

## Endpoint
POST /api/extractresume

## Request Body
```json
{
  "file_base64": "<base64 encoded file>",
  "file_type": "pdf"
}
```

## Response
```json
{
  "success": true,
  "file_type": "pdf",
  "page_count": 2,
  "ocr_used": false,
  "resume": {
    "extraction_confidence": "high",
    "candidate": { "name": "...", "current_title": "...", "email": "..." },
    "total_experience_years": 5,
    "skills": ["Python", "Azure", "SQL"],
    "skills_by_category": { "programming": [...], "cloud_devops": [...] },
    "experience": [{ "title": "...", "company": "...", "years": 3 }],
    "education": [{ "degree": "...", "institution": "...", "year": 2018 }],
    "certifications": [],
    "languages": ["English"],
    "raw_sections": { "skills": "...", "experience": "..." }
  }
}
```

## Supported File Types
- PDF (.pdf) — including scanned PDFs with OCR fallback
- Word (.docx, .doc)
- Images (.jpg, .jpeg, .png, .tiff)

## Features
- Multi-column PDF layout detection
- 500+ skills across 18 categories (tech + non-tech + mixed)
- Accurate experience years (overlap-aware calculation)
- Confidence scores on all extracted fields
- Raw section text for Groq AI fallback
- sharan

## Deployment
Push this repository to Azure Functions via GitHub Actions or Azure DevOps.
