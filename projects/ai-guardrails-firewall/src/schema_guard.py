import json
import re
from typing import Tuple, Dict, Any, Optional

class SchemaGuard:
    """Validates and auto-repairs structured JSON outputs against schemas."""

    @staticmethod
    def validate_and_repair_json(raw_text: str, required_keys: Optional[list] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Validates JSON, strips markdown code fences if present, and verifies required schema keys."""
        text = raw_text.strip()
        # Strip markdown ```json ... ``` fences
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                return False, None, "Output is not a valid JSON object"
            
            if required_keys:
                missing = [k for k in required_keys if k not in parsed]
                if missing:
                    return False, parsed, f"Missing required keys: {missing}"
                    
            return True, parsed, "Valid JSON"
        except json.JSONDecodeError as e:
            # Simple repair attempt for unclosed braces or trailing commas
            try:
                fixed = re.sub(r",\s*}", "}", text)
                if not fixed.endswith("}"):
                    fixed += "}"
                parsed = json.loads(fixed)
                return True, parsed, "Auto-repaired JSON"
            except Exception:
                return False, None, f"JSON parse error: {str(e)}"
