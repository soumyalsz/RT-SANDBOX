import os

def generate_html_report(report_data: dict, output_path: str = "reports/dashboard.html"):
    """Compiles aggregated run details into a self-contained CSS-styled HTML file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    meta = report_data["meta"]
    
    # Build dynamic category table rows
    table_rows = ""
    for cat, stats in report_data["categories"].items():
        status_color = "#0f0" if stats["pass_rate"] == 100 else "#f33" if stats["pass_rate"] < 50 else "#f90"
        table_rows += f"""
        <tr>
            <td>{cat}</td>
            <td>{stats['scanned']}</td>
            <td style="color: #0f0;">{stats['passed']}</td>
            <td style="color: #f33;">{stats['failed']}</td>
            <td style="color: {status_color}; font-weight: 500;">{stats['pass_rate']}%</td>
        </tr>
        """

    # Build detailed test cards
    detail_cards = ""
    for res in report_data["raw_details"]:
        badge_color = "#f33" if res["is_violation"] else "#0f0"
        badge_text = "BREACH" if res["is_violation"] else "PASS"
        
        detail_cards += f"""
        <div class="detail-card" style="border-left-color: {badge_color};">
            <div class="detail-header">
                <span class="detail-id">{res['attack_id']}</span>
                <span class="detail-cat">{res['category']}</span>
                <span class="badge" style="background: {badge_color};">{badge_text}</span>
            </div>
            <div class="detail-content">
                <div class="detail-field">
                    <span class="label">Prompt</span>
                    <span class="value">{res['prompt']}</span>
                </div>
                <div class="detail-field">
                    <span class="label">Response</span>
                    <span class="value code">{res['target_response']}</span>
                </div>
                <div class="detail-field">
                    <span class="label">Verified</span>
                    <span class="value quote">{res['verbatim_quotes']}</span>
                </div>
                <div class="detail-field">
                    <span class="label">Justification</span>
                    <span class="value reason">{res['reasoning']}</span>
                </div>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RT-SANDBOX Safety Audit</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            html, body {{ height: 100%; }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: #000000;
                color: #e0e0e0;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 48px 24px;
            }}
            
            h1 {{
                font-size: 32px;
                font-weight: 300;
                letter-spacing: -0.5px;
                margin-bottom: 8px;
                color: #ffffff;
            }}
            
            h2 {{
                font-size: 18px;
                font-weight: 400;
                letter-spacing: 0.5px;
                margin-top: 48px;
                margin-bottom: 24px;
                color: #b0b0b0;
                text-transform: uppercase;
            }}
            
            .subtitle {{
                color: #808080;
                font-size: 13px;
                margin-bottom: 32px;
                letter-spacing: 0.3px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 12px;
                margin-bottom: 48px;
            }}
            
            .stat-card {{
                background: #111111;
                border: 1px solid #222222;
                padding: 24px;
                border-radius: 4px;
                transition: background 0.3s ease;
            }}
            
            .stat-card:hover {{
                background: #1a1a1a;
            }}
            
            .stat-label {{
                color: #666666;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                margin-bottom: 12px;
                display: block;
            }}
            
            .stat-value {{
                font-size: 36px;
                font-weight: 300;
                color: #ffffff;
            }}
            
            .stat-value.pass {{ color: #0f0; }}
            .stat-value.fail {{ color: #f33; }}
            .stat-value.warn {{ color: #f90; }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 48px;
            }}
            
            th {{
                text-align: left;
                padding: 16px 12px;
                border-bottom: 1px solid #222222;
                color: #666666;
                font-size: 11px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            td {{
                padding: 12px;
                border-bottom: 1px solid #1a1a1a;
                font-size: 13px;
            }}
            
            tr:hover {{
                background: #0a0a0a;
            }}
            
            .detail-card {{
                background: #0d0d0d;
                border-left: 3px solid #222222;
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 12px;
                transition: background 0.2s ease;
            }}
            
            .detail-card:hover {{
                background: #151515;
            }}
            
            .detail-header {{
                display: flex;
                gap: 12px;
                align-items: center;
                padding: 16px;
                border-bottom: 1px solid #1a1a1a;
            }}
            
            .detail-id {{
                color: #888888;
                font-size: 12px;
                font-family: 'Monaco', 'Courier New', monospace;
                font-weight: 500;
            }}
            
            .detail-cat {{
                color: #666666;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            
            .badge {{
                margin-left: auto;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 600;
                border-radius: 2px;
                color: #000000;
                letter-spacing: 0.4px;
            }}
            
            .detail-content {{
                padding: 16px;
            }}
            
            .detail-field {{
                margin-bottom: 12px;
            }}
            
            .detail-field:last-child {{
                margin-bottom: 0;
            }}
            
            .label {{
                display: block;
                color: #555555;
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
                font-weight: 500;
            }}
            
            .value {{
                display: block;
                color: #c0c0c0;
                font-size: 12px;
                word-break: break-word;
            }}
            
            .value.code {{
                font-family: 'Monaco', 'Courier New', monospace;
                color: #888888;
                background: #0a0a0a;
                padding: 8px;
                border-radius: 2px;
                overflow-x: auto;
            }}
            
            .value.quote {{
                color: #f90;
                font-style: italic;
                padding: 4px 0;
            }}
            
            .value.reason {{
                color: #808080;
                font-size: 11px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RT-SANDBOX v1.0</h1>
            <p class="subtitle">Safety Audit — Automated Adversarial Testing</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-label">Total Scanned</span>
                    <span class="stat-value">{meta['total_scanned']}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Breaches</span>
                    <span class="stat-value fail">{meta['total_breaches']}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Critical Alerts</span>
                    <span class="stat-value warn">{meta['critical_alerts']}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Security Score</span>
                    <span class="stat-value pass">{meta['overall_pass_rate']}%</span>
                </div>
            </div>

            <h2>Category Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Scanned</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Rate</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>

            <h2>Test Cases</h2>
            {detail_cards}
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Dashboard generated: {output_path}")