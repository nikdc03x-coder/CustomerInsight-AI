"""Integration tests for all Customer Intelligence Platform UI pages."""

from pathlib import Path
import sys
import pytest
from streamlit.testing.v1 import AppTest

APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


@pytest.fixture(autouse=True)
def setup_app_path(monkeypatch):
    monkeypatch.syspath_prepend(str(APP_ROOT))


def test_data_workspace_page_runs():
    page_path = APP_ROOT / "pages/data_workspace.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Data Workspace" in app.title[0].value
    assert len(app.tabs) >= 2


def test_revenue_analytics_page_runs():
    page_path = APP_ROOT / "pages/revenue_analytics.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Revenue Analytics" in app.title[0].value
    assert len(app.metric) >= 5


def test_product_intelligence_page_runs():
    page_path = APP_ROOT / "pages/product_intelligence.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Product & Basket Intelligence" in app.title[0].value
    assert len(app.tabs) >= 2
    assert len(app.metric) >= 3


def test_predictive_intelligence_page_runs():
    page_path = APP_ROOT / "pages/predictive_intelligence.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Predictive CLV & Churn" in app.title[0].value
    assert len(app.metric) >= 4


def test_ai_data_assistant_page_runs():
    page_path = APP_ROOT / "pages/ai_data_assistant.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "AI Data Assistant" in app.title[0].value
    assert len(app.chat_message) >= 1


def test_business_insights_page_runs():
    page_path = APP_ROOT / "pages/business_insights_page.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Business Insights Engine" in app.title[0].value


def test_reports_exports_page_runs():
    page_path = APP_ROOT / "pages/reports_exports.py"
    app = AppTest.from_file(str(page_path), default_timeout=75).run()
    assert not app.exception
    assert "Reports & Exports" in app.title[0].value
    assert len(app.tabs) >= 2
