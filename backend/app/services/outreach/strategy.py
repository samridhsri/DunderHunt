from typing import Tuple

VALID_CHANNELS = ["LinkedIn", "Email", "Other"]
VALID_PURPOSES = ["Introduce myself", "Ask about the team", "Ask for advice", "Ask for referral"]

class OutreachStrategyService:
    @staticmethod
    def validate_strategy(channel: str, purpose: str) -> Tuple[str, str]:
        valid_chan = channel if channel in VALID_CHANNELS else "LinkedIn"
        valid_purp = purpose if purpose in VALID_PURPOSES else "Introduce myself"
        return valid_chan, valid_purp
