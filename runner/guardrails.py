import re
from typing import Tuple

# High-certainty indicators that a safety rule was bypassed or data was leaked
BANNED_OUTPUT_SIGNATURES = [
    r"system compromised",
    r"override successful",
    r"security bypass confirmed",
]

def scan_output_guardrail(raw_llm_output: str) -> Tuple[bool, str]:
    """
    Scans the raw text output from the target model before it reaches the user.
    If a critical security signature is found, it overrides the response.
    """
    cleaned_output = raw_llm_output.lower().strip()
    
    for pattern in BANNED_OUTPUT_SIGNATURES:
        if re.search(pattern, cleaned_output):
            # Guardrail triggers! Intercept and neutralize the leak.
            secured_fallback = (
                "[GUARDRAIL INTERCEPT] Safety violation detected in model output. "
                "Transmission terminated."
            )
            return True, secured_fallback
            
    # Output is safe, pass it through unchanged
    return False, raw_llm_output
