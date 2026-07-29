# Scoring Formula & Fit Engine Specification

## Scoring Philosophy
Scoring is designed to produce consistent, objective ranking across jobs rather than arbitrary precision.

## Layer 1: Deterministic Filtering Rules
Executed before calling LLMs. Violations result in automatic hard score caps or instant `SKIP` recommendations:
1. **Work Authorization**: Hard fail if job explicitly requires US Citizenship / Security Clearance and candidate lacks it.
2. **Employment Type / Role Level**: Internship cap if candidate targets full-time roles, or vice versa.
3. **Company Exclusions**: Instant `SKIP` if company is on candidate's excluded list.
4. **Location Preference**: Hard penalty if candidate requests Remote Only and job is strictly On-Site in an unapproved city.

## Layer 2: Scoring Weights (0 - 100 Overall Score)
- **Technical Fit (30%)**: Skill overlap, framework proficiency, language match.
- **Role Alignment (20%)**: Target role title match, responsibilities, team function.
- **Experience Level (15%)**: Years of experience, expected career stage.
- **Work Authorization (15%)**: Visa sponsorship availability / authorization match.
- **Location (10%)**: Remote, Hybrid, or On-site city alignment.
- **Career Value (5%)**: Company reputation, growth potential, technology stack quality.
- **Application Effort (5%)**: Ease of application process.

## Priority Thresholds
- **90 – 100**: Priority **A** -> Recommendation: `APPLY`
- **80 – 89**: Priority **B** -> Recommendation: `APPLY` / `REVIEW`
- **70 – 79**: Priority **C** -> Recommendation: `SAVE`
- **< 70**: Priority **Skip** -> Recommendation: `SKIP`
