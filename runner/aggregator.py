from typing import List, Dict, Any

def aggregate_run_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Groups individual test executions by safety categories and calculates
    aggregated pass rates and critical vulnerability flags.
    """
    total_scanned = len(results)
    total_breaches = 0
    critical_alerts = 0
    
    # Initialize per-category metrics grid
    category_summary: Dict[str, Dict[str, Any]] = {}

    # --- LOOP 1: Process individual results ---
    for res in results:
        cat = res["category"]
        is_breach = res["is_violation"]
        severity = res["severity"].lower()
        
        if cat not in category_summary:
            category_summary[cat] = {"scanned": 0, "passed": 0, "failed": 0}
            
        category_summary[cat]["scanned"] += 1
        
        if is_breach:
            category_summary[cat]["failed"] += 1
            total_breaches += 1
            if severity == "critical" or severity == "high":
                critical_alerts += 1
        else:
            category_summary[cat]["passed"] += 1

    # --- LOOP 2: Calculate precise category percentages ---
    # This must sit COMPLETELY outside of Loop 1 (aligned to the far left)
    for cat, stats in category_summary.items():
        stats["pass_rate"] = round((stats["passed"] / stats["scanned"]) * 100, 2)

    # --- FINAL RETURN: Ships the final payload ---
    # This must also be aligned to the far left so it only runs AFTER both loops finish
    return {
        "meta": {
            "total_scanned": total_scanned,
            "total_breaches": total_breaches,
            "critical_alerts": critical_alerts,
            "overall_pass_rate": round(((total_scanned - total_breaches) / total_scanned) * 100, 2) if total_scanned > 0 else 100.0
        },
        "categories": category_summary,
        "raw_details": results
    }