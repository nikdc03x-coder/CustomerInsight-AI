"""Exercise the validation page with isolated evidence and real Streamlit widgets."""

from pathlib import Path
import shutil
import sys

import pandas as pd
import pytest


pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest


@pytest.fixture
def validation_page(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    app = tmp_path / "app"
    (app / "pages").mkdir(parents=True)
    for name in ["dashboard_ui.py", "k2_diagnostics.py", "pages/model_validation_studio.py"]:
        shutil.copy2(root / "app" / name, app / name)
    monkeypatch.syspath_prepend(str(app))
    monkeypatch.delitem(sys.modules, "k2_diagnostics", raising=False)
    monkeypatch.delitem(sys.modules, "dashboard_ui", raising=False)
    results = tmp_path / "results/experiments"
    results.mkdir(parents=True)
    pd.DataFrame([
        {
            "preprocessing": method, "clusters": k,
            "silhouette": 0.5, "ari_vs_baseline": 0.8, "inertia": 100 / k,
        }
        for method in ["Standard scaling", "Log + standard scaling"]
        for k in range(2, 11)
    ]).to_csv(results / "model_validation_results.csv", index=False)
    pd.DataFrame({
        "cluster": [0, 1], "customers": [90, 10],
        "median_recency": [20, 5], "median_frequency": [2, 30],
        "median_monetary": [100, 4000], "customer_share_pct": [90, 10],
    }).to_csv(results / "k2_cluster_diagnostics.csv", index=False)
    return app / "pages/model_validation_studio.py"


def test_validation_diagnostic_renders_once_and_survives_interaction(validation_page):
    app = AppTest.from_file(str(validation_page), default_timeout=20).run()
    assert not app.exception
    assert sum(
        header.value == "When a High Score Can Be Misleading" for header in app.header
    ) == 1
    assert len(app.selectbox(key="k2_diagnostics_metric_selector").options) == 3
    app.selectbox(key="k2_diagnostics_metric_selector").select(
        "Positive spending (£)"
    ).run()
    assert not app.exception
    assert sum(
        header.value == "When a High Score Can Be Misleading" for header in app.header
    ) == 1


def test_validation_missing_results_stops_with_guidance(validation_page):
    results = (
        validation_page.parents[2] / "results/experiments/model_validation_results.csv"
    )
    results.unlink()
    app = AppTest.from_file(str(validation_page), default_timeout=20).run()
    assert not app.exception
    assert any("not available" in warning.value for warning in app.warning)
    assert not app.header


def test_dashboard_registers_every_page_and_links_to_each_workspace(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    app_dir = tmp_path / "app"
    shutil.copytree(root / "app", app_dir, ignore=shutil.ignore_patterns("__pycache__"))
    monkeypatch.syspath_prepend(str(app_dir))
    monkeypatch.delitem(sys.modules, "dashboard_ui", raising=False)
    app = AppTest.from_file(str(app_dir / "main.py"), default_timeout=20).run()
    assert not app.exception
    assert app.title[0].value == "Dashboard"
    registered = {
        Path(info["script_path"]).relative_to(app_dir).as_posix()
        for info in app._registered_pages.values() if info.get("script_path")
    }
    assert registered == {
        "pages/research_overview.py", "pages/retail_data_explorer.py",
        "pages/rfm_intelligence.py", "customer_insights.py",
        "pages/research_findings.py", "pages/model_validation_studio.py",
        "pages/research_health.py", "pages/data_workspace.py",
        "pages/revenue_analytics.py", "pages/product_intelligence.py",
        "pages/predictive_intelligence.py", "pages/ai_data_assistant.py",
        "pages/business_insights_page.py", "pages/reports_exports.py",
    }
    assert len(app.get("page_link")) == 12
    # Missing local research files must leave all workspaces accessible.
    assert len(app.metric) == 4


def test_chart_theme_preserves_values_and_series(monkeypatch):
    import plotly.graph_objects as go
    from dashboard_ui import show_chart

    figure = go.Figure(go.Bar(x=["A", "B"], y=[12, 7], name="Customers"))
    original = figure.to_plotly_json()["data"]
    captured = []
    monkeypatch.setattr("streamlit.plotly_chart", lambda chart, **kwargs: captured.append(chart))
    show_chart(figure, width="stretch")
    assert captured[0].to_plotly_json()["data"] == original
