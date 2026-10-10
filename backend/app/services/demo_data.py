import os
from typing import List, Optional
from pathlib import Path
from ..schemas.audit import SyntheticScenario, AdInput

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SAMPLE_PAGES_DIR = BASE_DIR / "sample_data" / "pages"

SYNTHETIC_SCENARIOS: List[SyntheticScenario] = [
    SyntheticScenario(
        id="strong_match",
        name="Scenario 1: Strong Match (Agile Project Management)",
        label="Synthetic example",
        category="High Alignment Benchmark",
        mismatch_description="Headline, 99.9% uptime, 14-day free trial, and primary CTA match verbatim on the target page.",
        ad=AdInput(
            headline="Modern Project Management Software for Agile Teams",
            description="Automate sprint planning and track roadmaps with 99.9% uptime. Includes 14-day free trial.",
            cta="Start 14-Day Free Trial"
        ),
        html_file_path="scenario_1_strong_match.html"
    ),
    SyntheticScenario(
        id="missing_material",
        name="Scenario 2: Missing Material Promise (50% Off & Free Domain)",
        label="Synthetic example",
        category="Missing Material Promise",
        mismatch_description="Ad promises 50% Off first year, Free Domain, and 24/7 phone support, but landing page completely omits these offers.",
        ad=AdInput(
            headline="Cloud Hosting - 50% Off First Year & Free Domain",
            description="Deploy worldwide with zero configuration. Includes unlimited SSL certificates and 24/7 phone support.",
            cta="Claim 50% Discount"
        ),
        html_file_path="scenario_2_missing_material.html"
    ),
    SyntheticScenario(
        id="partial_support",
        name="Scenario 3: Partial Support (Enterprise Security Platform)",
        label="Synthetic example",
        category="Partial Support & Metric Gap",
        mismatch_description="Vulnerability scanning and enterprise security are present, but specific ad figures (1,000+ endpoints, under 5 minutes) are unconfirmed.",
        ad=AdInput(
            headline="Enterprise Security Platform - Protect 1,000+ Endpoints",
            description="Automated vulnerability scanning with instant Slack alerts and automated remediation in under 5 minutes.",
            cta="Explore Platform"
        ),
        html_file_path="scenario_3_partial_support.html"
    ),
    SyntheticScenario(
        id="explicit_contradiction",
        name="Scenario 4: Explicit Contradiction (Free vs Paid & No Refunds)",
        label="Synthetic example",
        category="Explicit Factual Contradiction",
        mismatch_description="Ad promises free forever with no credit card and 100% money-back guarantee; page explicitly states paid subscription required and strict non-refundable terms.",
        ad=AdInput(
            headline="Accounting Suite - Free Forever with No Credit Card Required",
            description="Unlimited invoices and 100% money-back guarantee with instant cancellation anytime.",
            cta="Sign Up Free"
        ),
        html_file_path="scenario_4_contradiction.html"
    ),
    SyntheticScenario(
        id="inaccessible_website",
        name="Scenario 5: Inaccessible Website (Empty JS Shell Error)",
        label="Synthetic example",
        category="Extraction Failure & Inaccessible Page",
        mismatch_description="Target URL serves a client-side empty JavaScript shell without server-rendered content, triggering an extraction error, null score, and no analyzed findings.",
        ad=AdInput(
            headline="Apex Analytics - Real-Time Customer Insights",
            description="Track conversion funnels and user retention in real-time.",
            cta="Get Started"
        ),
        html_file_path="scenario_5_empty_shell.html",
        simulated_error="insufficient_content"
    ),
    SyntheticScenario(
        id="cta_mismatch",
        name="Scenario 6: CTA Mismatch (Free Trial vs Sales Consultation)",
        label="Synthetic example",
        category="Action / CTA Friction",
        mismatch_description="Ad copy promises an immediate self-serve 'Start Free Trial Now', but landing page primary action demands 'Schedule Sales Consultation'.",
        ad=AdInput(
            headline="HR Payroll Automation Software",
            description="Run payroll in 3 clicks with automated tax filing and compliance reports.",
            cta="Start Free Trial Now"
        ),
        html_file_path="scenario_6_cta_mismatch.html"
    ),
    SyntheticScenario(
        id="uncertain_evidence",
        name="Scenario 7: Uncertain Evidence (Vague Tech Buzzwords)",
        label="Synthetic example",
        category="Uncertain & Ambiguous Match",
        mismatch_description="Ad asserts technical edge consensus claims, but landing page contains only high-level conceptual buzzwords.",
        ad=AdInput(
            headline="Quantum Edge Computing for Autonomous Fleet Networks",
            description="Sub-millisecond latency fabric with decentralized consensus algorithms.",
            cta="Learn More"
        ),
        html_file_path="scenario_7_uncertain.html"
    )
]

def load_scenario_html(scenario: SyntheticScenario) -> str:
    """
    Reads the real HTML file from sample_data/pages/ ensuring no demo result is hardcoded.
    """
    if not scenario.html_file_path:
        return ""
    file_path = SAMPLE_PAGES_DIR / scenario.html_file_path
    if not file_path.exists():
        raise FileNotFoundError(f"Sample HTML file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")

def get_scenario_by_id(scenario_id: str) -> Optional[SyntheticScenario]:
    for s in SYNTHETIC_SCENARIOS:
        if s.id == scenario_id:
            return s
    return None
