# Resume Analysis Schema

v0.3.2 이력서 분석 schema는 다음 구조를 사용한다.

- `summary`
- `headline`
- `skills`
- `experiences`
- `projects`
- `education`
- `certifications`
- `achievements`
- `awards`
- `portfolio_links`
- `languages`
- `contact`
- `other_sections`
- `keywords`
- `warnings`
- `confidence`

핵심 항목 evidence:

- `source_text`
- `start_offset`
- `end_offset`
- `page_number`
- `section_candidate`
- `extraction_id`

구현 파일:

- `backend/app/schemas/resume_analysis.py`
