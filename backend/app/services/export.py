import io
import csv
import json
import html
from typing import Dict, Any
from ..schemas.audit import AuditResponse

def sanitize_csv_cell(value: Any) -> str:
    """
    Prevents CSV Formula Injection (CWE-1236) by prepending a single quote
    if the string starts with =, +, -, @, tab, or carriage return.
    """
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{text}"
    return text

def generate_csv_claims(audit: AuditResponse) -> str:
    """
    Generates CSV export of claims with formula injection mitigation.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Claim ID", "Source Part", "Category", "Claim Text",
        "Status", "Similarity %", "Verified Evidence Quote",
        "Quote Verified", "Element Provenance", "Status Reason", "Suggested Action"
    ])
    for c in audit.claims:
        writer.writerow([
            sanitize_csv_cell(c.claim_id),
            sanitize_csv_cell(c.source_part),
            sanitize_csv_cell(c.category.value if hasattr(c.category, "value") else c.category),
            sanitize_csv_cell(c.claim_text),
            sanitize_csv_cell(c.status.value if hasattr(c.status, "value") else c.status),
            sanitize_csv_cell(f"{c.similarity_score:.1f}"),
            sanitize_csv_cell(c.evidence_quote or "No verified evidence quote available."),
            sanitize_csv_cell("Yes" if c.is_quote_verified else "No"),
            sanitize_csv_cell(c.quote_source_element or "none"),
            sanitize_csv_cell(c.status_reason),
            sanitize_csv_cell(c.suggested_action)
        ])
    return output.getvalue()

def generate_markdown_report(audit: AuditResponse) -> str:
    lines = []
    lines.append("# Message Match Audit Report")
    if audit.is_synthetic_demo:
        lines.append("> ⚠️ **Notice**: This is a **Synthetic example** demo scenario for evaluation purposes.\n")
    
    score_display = f"{audit.overall_score:.1f} / 100" if audit.overall_score is not None else "Score unavailable"
    lines.append(f"**Overall Score:** {score_display} (Grade: {audit.grade or 'N/A'})")
    lines.append(f"**Verdict:** {audit.summary_verdict or 'N/A'}\n")

    if audit.score_breakdown:
        lines.append("## Score Formula & Breakdown")
        lines.append(f"> {audit.score_breakdown.formula_text}\n")
        lines.append(f"- **Headline to Hero Alignment:** {audit.score_breakdown.headline_hero_alignment}/100")
        lines.append(f"- **CTA Alignment:** {audit.score_breakdown.cta_alignment}/100")
        lines.append(f"- **Claim Coverage Rate:** {audit.score_breakdown.claim_coverage_rate}/100")
        lines.append(f"- **Offer Consistency:** {audit.score_breakdown.offer_consistency}/100")
        if audit.score_breakdown.contradiction_penalty > 0:
            lines.append(f"- **Penalties Applied:** -{audit.score_breakdown.contradiction_penalty} pts")
        if audit.score_breakdown.is_capped_at_40:
            lines.append("- **Hard Cap Applied:** Score capped at 40.0 due to contradictory claims.")
        lines.append("")

    if audit.cta_analysis:
        lines.append("## CTA Continuity Analysis")
        lines.append(f"- **Ad CTA:** `{audit.cta_analysis.ad_cta or 'None'}`")
        lines.append(f"- **Landing Page Primary CTA:** `{audit.cta_analysis.page_primary_cta or 'None'}`")
        lines.append(f"- **CTA Match Status:** {audit.cta_analysis.match_status.value}")
        lines.append(f"- **Friction Note:** {audit.cta_analysis.friction_notes}\n")

    lines.append("## Claim Verification Breakdown")
    lines.append("| ID | Source | Category | Claim | Status | Sim % | Verified Quote |")
    lines.append("|---|---|---|---|---|---|---|")
    for c in audit.claims:
        quote = c.evidence_quote if c.is_quote_verified else "No verified evidence quote available."
        clean_quote = quote.replace("|", "/")
        cat_val = c.category.value if hasattr(c.category, "value") else c.category
        stat_val = c.status.value if hasattr(c.status, "value") else c.status
        lines.append(f"| {c.claim_id} | {c.source_part} | {cat_val} | {c.claim_text} | {stat_val} | {c.similarity_score:.0f}% | {clean_quote} |")
    lines.append("")

    if audit.recommendations:
        lines.append("## Prioritized Action Recommendations")
        for rec in audit.recommendations:
            p_val = rec.priority.value if hasattr(rec.priority, "value") else rec.priority
            lines.append(f"### [{p_val}] {rec.category}: {rec.issue}")
            lines.append(f"- **Impact:** {rec.impact}")
            lines.append(f"- **Recommended Fix:** {rec.recommended_fix}")
            if rec.suggested_page_copy:
                lines.append(f"- **Suggested Page Copy:** `{rec.suggested_page_copy}`")
            if rec.suggested_ad_copy:
                lines.append(f"- **Suggested Ad Copy:** `{rec.suggested_ad_copy}`")
            lines.append("")

    lines.append("\n*Generated deterministically by PS-03 Message Match Auditor*")
    return "\n".join(lines)

def generate_self_contained_html_report(audit: AuditResponse) -> str:
    """
    Generates a standalone, self-contained HTML report with all text HTML-escaped.
    """
    def esc(text: Any) -> str:
        if text is None:
            return ""
        return html.escape(str(text))

    score_display = f"{audit.overall_score:.1f}" if audit.overall_score is not None else "Unavailable"
    
    claims_rows = ""
    for c in audit.claims:
        cat_val = c.category.value if hasattr(c.category, "value") else c.category
        stat_val = c.status.value if hasattr(c.status, "value") else c.status
        quote_style = "color: #059669; font-style: italic;" if c.is_quote_verified else "color: #6b7280;"
        claims_rows += f"""
        <tr>
            <td><code>{esc(c.claim_id)}</code></td>
            <td>{esc(c.source_part)}</td>
            <td><span class="badge">{esc(cat_val)}</span></td>
            <td><strong>{esc(c.claim_text)}</strong></td>
            <td><span class="status status-{esc(stat_val).lower().replace(' ', '-')}">{esc(stat_val)}</span></td>
            <td>{c.similarity_score:.0f}%</td>
            <td style="{quote_style}">"{esc(c.evidence_quote or 'No verified evidence quote available.')}"</td>
        </tr>
        """

    rec_cards = ""
    for r in audit.recommendations:
        p_val = r.priority.value if hasattr(r.priority, "value") else r.priority
        rec_cards += f"""
        <div class="card rec-card rec-{esc(p_val).lower()}">
            <div class="rec-header">
                <span class="priority-badge">{esc(p_val)} PRIORITY</span>
                <strong>{esc(r.category)}</strong>
            </div>
            <h4>{esc(r.issue)}</h4>
            <p><strong>Impact:</strong> {esc(r.impact)}</p>
            <div class="fix-box"><strong>Fix:</strong> {esc(r.recommended_fix)}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Message Match Audit Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 40px; background: #f8fafc; color: #1e293b; line-height: 1.5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #ffffff; padding: 32px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
        h1, h2, h3, h4 {{ color: #0f172a; margin-top: 0; }}
        .header-meta {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 24px; }}
        .demo-alert {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 10px 16px; border-radius: 8px; font-weight: 600; margin-bottom: 20px; }}
        .score-box {{ display: flex; align-items: center; gap: 24px; background: #f1f5f9; padding: 20px; border-radius: 8px; margin-bottom: 24px; }}
        .score-val {{ font-size: 42px; font-weight: 800; color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #f8fafc; color: #475569; }}
        .badge {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        .status {{ padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }}
        .status-supported {{ background: #d1fae5; color: #065f46; }}
        .status-partial-match {{ background: #fef3c7; color: #92400e; }}
        .status-not-found {{ background: #f1f5f9; color: #475569; }}
        .status-contradicted {{ background: #fee2e2; color: #991b1b; }}
        .status-uncertain {{ background: #ede9fe; color: #5b21b6; }}
        .card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
        .rec-card {{ border-left: 4px solid #3b82f6; }}
        .rec-high {{ border-left-color: #ef4444; }}
        .rec-medium {{ border-left-color: #f59e0b; }}
        .fix-box {{ background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; margin-top: 8px; }}
        .footer {{ margin-top: 32px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-meta">
            <h1>PS-03 Ad-to-Landing-Page Message Match Audit Report</h1>
            <div>Extraction Source: <strong>{esc(audit.source_description)}</strong></div>
            <div>Generated: {esc(audit.timestamp)}</div>
        </div>

        {f'<div class="demo-alert">⚠️ Synthetic example: Pre-configured demonstration scenario.</div>' if audit.is_synthetic_demo else ''}

        <div class="score-box">
            <div>
                <div class="score-val">{score_display}</div>
                <div>Overall Quality Score</div>
            </div>
            <div>
                <div><strong>Grade:</strong> {esc(audit.grade or 'N/A')}</div>
                <div><strong>Verdict:</strong> {esc(audit.summary_verdict or 'N/A')}</div>
            </div>
        </div>

        <h2>Atomic Claim Audit Findings</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th><th>Source</th><th>Category</th><th>Claim</th><th>Status</th><th>Similarity</th><th>Verified Evidence Quote</th>
                </tr>
            </thead>
            <tbody>
                {claims_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 32px;">Prioritized Recommendations</h2>
        {rec_cards}

        <div class="footer">
            Generated by PS-03 Message Match Auditor &bull; Deterministic Substring Quote Provenance Enforced
        </div>
    </div>
</body>
</html>"""
