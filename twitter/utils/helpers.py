# twitter/utils/helpers.py
import re
import json
from typing import Optional
from datetime import datetime
from dataclasses import is_dataclass, asdict

def sanitize_text(text: str) -> str:
    """Clean text from extra whitespace and control characters"""
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def parse_relative_date(time_str: str) -> Optional[int]:
    """Parse relative time string (e.g., 2h) to hours"""
    match = re.match(r'(\d+)([hmd])', time_str)
    if not match:
        return None
    
    value, unit = match.groups()
    multipliers = {'h': 1, 'm': 1/60, 'd': 24}
    return int(value) * multipliers.get(unit, 1)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)