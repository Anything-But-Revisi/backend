## ADDED Requirements

### Requirement: generate_report_draft Function
The system SHALL provide a generate_report_draft(report_data: ReportCreate) → str function in app/services/report.py that calls Gemini 2.5 Flash LLM and returns formatted report narrative.

#### Scenario: Generate report narrative from structured input
- **WHEN** generate_report_draft is called with location="kampus", perpetrator="lecturer", description="inappropriate comments", evidence="witness", user_goal="document safely"
- **THEN** function returns a formatted report narrative in Indonesian following "FORMULIR PENGADUAN KEKERASAN SEKSUAL" structure with sections: Identifikasi Kebutuhan, Identifikasi Pelaku, Kronologi Kejadian, Bukti Terlampir
  
#### Scenario: Report uses first-person perspective
- **WHEN** generate_report_draft generates a narrative
- **THEN** generated_document uses first-person perspective ("Saya") throughout the narrative

#### Scenario: System prompt enforces consistent structure
- **WHEN** generate_report_draft calls Gemini API
- **THEN** system prompt includes static instructions enforcing the four-section SEXUAL VIOLENCE COMPLAINT FORM structure and prevents deviation

#### Scenario: Function handles Gemini API errors gracefully
- **WHEN** Gemini API returns an error (rate limit, timeout, authentication failure)
- **THEN** function raises an exception with meaningful error message (does not hide the error)

### Requirement: LLM Parameters
The system SHALL configure Gemini 2.5 Flash with temperature=0.3 to minimize output variance and ensure consistent report formatting.

#### Scenario: Temperature setting ensures consistency
- **WHEN** generate_report_draft is called multiple times with identical input
- **THEN** generated narratives are similar in structure and content (low creativity mode)
