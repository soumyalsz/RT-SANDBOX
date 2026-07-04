from runner.judge import JudgeVerdict

def validate_judge_citations(target_response: str, verdict: JudgeVerdict) -> tuple[bool, JudgeVerdict]:
    if not verdict.is_violation:
        return True, verdict

    sanitized_quotes = []
    for quote in verdict.verbatim_quotes:
        clean_quote = quote.strip()
        if clean_quote in target_response and clean_quote:
            sanitized_quotes.append(clean_quote)
            
    if verdict.is_violation and not sanitized_quotes and verdict.verbatim_quotes:
        verdict.is_violation = False
        verdict.reasoning = f"VERDICT INVALIDATED: Evidence quotes failed substring verification."
    
    verdict.verbatim_quotes = sanitized_quotes
    return (len(sanitized_quotes) > 0 or not verdict.verbatim_quotes), verdict