import io
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.demo_data import SYNTHETIC_SCENARIOS, load_scenario_html

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_get_all_7_demo_scenarios():
    """Requirement 2: Exactly 7 labeled 'Synthetic example' scenarios."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/demo")
        assert res.status_code == 200
        scenarios = res.json()
        assert len(scenarios) == 7
        for s in scenarios:
            assert s["label"] == "Synthetic example"

@pytest.mark.asyncio
async def test_get_demo_scenario_by_id():
    """Requirement 1: GET /api/demo/{id}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/demo/strong_match")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "strong_match"
        assert len(data["html_content"]) > 100

        # Non-existent ID returns 404
        res404 = await client.get("/api/demo/non_existent_scenario")
        assert res404.status_code == 404

@pytest.mark.asyncio
async def test_all_7_scenarios_run_through_real_pipeline():
    """Requirement 2: Verify that each of the 7 scenarios runs through the real pipeline and is not hardcoded."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Scenario 1: strong match -> High score (>85), Grade A
        s1 = SYNTHETIC_SCENARIOS[0]
        html1 = load_scenario_html(s1)
        r1 = await client.post("/api/audit", json={"ad": s1.ad.model_dump(), "html_content": html1, "is_synthetic_demo": True})
        d1 = r1.json()
        assert d1["success"] is True
        assert d1["overall_score"] is not None and d1["overall_score"] >= 85.0
        assert d1["grade"] == "A"
        assert d1["supported_count"] >= 3

        # 2. Scenario 2: missing material promise -> Material offer claims missing
        s2 = SYNTHETIC_SCENARIOS[1]
        html2 = load_scenario_html(s2)
        r2 = await client.post("/api/audit", json={"ad": s2.ad.model_dump(), "html_content": html2, "is_synthetic_demo": True})
        d2 = r2.json()
        assert d2["success"] is True
        assert d2["not_found_count"] >= 1
        assert d2["overall_score"] < 80.0

        # 3. Scenario 3: partial support
        s3 = SYNTHETIC_SCENARIOS[2]
        html3 = load_scenario_html(s3)
        r3 = await client.post("/api/audit", json={"ad": s3.ad.model_dump(), "html_content": html3, "is_synthetic_demo": True})
        d3 = r3.json()
        assert d3["success"] is True
        assert d3["partial_count"] >= 1

        # 4. Scenario 4: explicit contradiction -> score capped at 40
        s4 = SYNTHETIC_SCENARIOS[3]
        html4 = load_scenario_html(s4)
        r4 = await client.post("/api/audit", json={"ad": s4.ad.model_dump(), "html_content": html4, "is_synthetic_demo": True})
        d4 = r4.json()
        assert d4["success"] is True
        assert d4["contradicted_count"] >= 1
        assert d4["overall_score"] <= 40.0
        assert d4["score_breakdown"]["is_capped_at_40"] is True

        # 5. Scenario 5: inaccessible website / empty shell -> fails extraction, null score, no findings (Rule 2)
        s5 = SYNTHETIC_SCENARIOS[4]
        html5 = load_scenario_html(s5)
        r5 = await client.post("/api/audit", json={"ad": s5.ad.model_dump(), "html_content": html5, "is_synthetic_demo": True})
        d5 = r5.json()
        assert d5["success"] is False
        assert d5["error_type"] == "EXTRACTION_FAILED"
        assert d5["overall_score"] is None
        assert len(d5["claims"]) == 0

        # 6. Scenario 6: CTA mismatch
        s6 = SYNTHETIC_SCENARIOS[5]
        html6 = load_scenario_html(s6)
        r6 = await client.post("/api/audit", json={"ad": s6.ad.model_dump(), "html_content": html6, "is_synthetic_demo": True})
        d6 = r6.json()
        assert d6["success"] is True
        assert d6["cta_analysis"]["friction_detected"] is True

        # 7. Scenario 7: uncertain evidence
        s7 = SYNTHETIC_SCENARIOS[6]
        html7 = load_scenario_html(s7)
        r7 = await client.post("/api/audit", json={"ad": s7.ad.model_dump(), "html_content": html7, "is_synthetic_demo": True})
        d7 = r7.json()
        assert d7["success"] is True
        assert d7["uncertain_count"] >= 1

@pytest.mark.asyncio
async def test_audit_snapshot_multipart_endpoint():
    """Requirement 1: POST /api/audit/snapshot."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        html_bytes = b"<html><body><h1>Test Snapshot Platform</h1><p>Comprehensive test description for snapshot analysis with sufficient text content for automated page parsing and claim matching.</p><button class='btn'>Click Here</button></body></html>"
        files = {"html_file": ("test_page.html", html_bytes, "text/html")}
        data = {
            "headline": "Test Snapshot Platform",
            "description": "Comprehensive test description for snapshot analysis with sufficient text content.",
            "cta": "Click Here"
        }
        res = await client.post("/api/audit/snapshot", data=data, files=files)
        assert res.status_code == 200
        res_data = res.json()
        assert res_data["success"] is True
        assert res_data["overall_score"] is not None

@pytest.mark.asyncio
async def test_export_formats_and_formula_injection_escaping():
    """Requirement 1 & 9: POST /api/export/{csv|json|html} with formula injection protection."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        s1 = SYNTHETIC_SCENARIOS[0]
        html1 = load_scenario_html(s1)
        audit_res = await client.post("/api/audit", json={"ad": s1.ad.model_dump(), "html_content": html1, "is_synthetic_demo": True})
        audit_data = audit_res.json()

        # Inject formula characters into a claim to test escaping
        audit_data["claims"][0]["claim_text"] = "=cmd|' /C calc'!A0"

        # 1. CSV export check
        csv_res = await client.post("/api/export/csv", json=audit_data)
        assert csv_res.status_code == 200
        # Formula cell MUST be sanitized by prepending a single quote
        assert "'=cmd|" in csv_res.text

        # 2. HTML self-contained export check
        html_res = await client.post("/api/export/html", json=audit_data)
        assert html_res.status_code == 200
        assert "<!DOCTYPE html>" in html_res.text
        assert "PS-03 Ad-to-Landing-Page Message Match Audit Report" in html_res.text
        # Must be HTML escaped
        assert "=cmd|" in html_res.text

        # 3. JSON export check
        json_res = await client.post("/api/export/json", json=audit_data)
        assert json_res.status_code == 200
        assert json_res.json()["success"] is True
