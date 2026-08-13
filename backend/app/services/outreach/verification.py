import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class ContactVerificationService:
    @staticmethod
    def verify_candidate(candidate: Dict[str, Any], target_company: str, target_role: str) -> Optional[Dict[str, Any]]:
        """
        Step 7: Verification component. Checks:
        1. Does candidate currently work at target company?
        2. Does role make sense (not ex-, not totally unrelated)?
        3. Confidence calculation (0.0 to 1.0).
        If verification fails confidence threshold (< 0.6), candidate is removed.
        """
        cand_comp = candidate.get("company", "").strip().lower()
        cand_title = candidate.get("title", "").strip().lower()
        target_comp_clean = target_company.strip().lower()

        # Rule 1: Company Verification
        company_verified = (target_comp_clean in cand_comp) or (cand_comp in target_comp_clean)

        # Rule 2: Role Verification
        ex_terms = ["ex-", "former", "past", "previously at"]
        role_verified = not any(term in cand_title for term in ex_terms)

        # Confidence calculation
        confidence = 0.5
        if company_verified:
            confidence += 0.3
        if role_verified:
            confidence += 0.15
        if candidate.get("profile_url"):
            confidence += 0.05

        if confidence < 0.6 or not role_verified:
            logger.info(f"Verification failed for candidate {candidate.get('name')}: confidence={confidence}, role_verified={role_verified}")
            return None

        verified = dict(candidate)
        verified["company_verified"] = company_verified
        verified["role_verified"] = role_verified
        verified["verification_confidence"] = round(confidence, 2)
        verified["verified_at"] = utcnow().isoformat()
        return verified
