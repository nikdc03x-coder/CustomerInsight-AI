"""CustomerInsight AI — Customer Intelligence Platform."""

__version__ = "0.2.0"

from customerinsight.schema import (
    CANONICAL_FIELDS,
    detect_column_mappings,
    coerce_canonical_types,
    assess_capabilities,
)
from customerinsight.cleaning import (
    audit_data_quality,
    clean_canonical_transactions,
    CleaningSummary,
)
from customerinsight.datasets import (
    list_datasets,
    get_dataset_metadata,
    load_dataset_transactions,
    register_uploaded_dataset,
    delete_dataset,
    DEFAULT_DATASET_ID,
)
from customerinsight.analytics import (
    calculate_rfm,
    get_revenue_kpis,
    get_revenue_trend,
    get_revenue_by_country,
    get_top_customers,
    segment_customers,
    compare_segments,
)
from customerinsight.products import (
    get_product_rankings,
    get_lowest_performing_products,
    run_market_basket_analysis,
)
from customerinsight.prediction import (
    assess_predictive_eligibility,
    predict_customer_recurrence_and_clv,
)
from customerinsight.ai_assistant import (
    ask_assistant,
    AssistantResponse,
    TOOL_REGISTRY,
)
from customerinsight.insights_engine import (
    generate_business_insights,
    BusinessInsight,
)
from customerinsight.reporting import (
    generate_executive_brief_markdown,
    export_customer_segments_csv,
)

__all__ = [
    "CANONICAL_FIELDS",
    "detect_column_mappings",
    "coerce_canonical_types",
    "assess_capabilities",
    "audit_data_quality",
    "clean_canonical_transactions",
    "CleaningSummary",
    "list_datasets",
    "get_dataset_metadata",
    "load_dataset_transactions",
    "register_uploaded_dataset",
    "delete_dataset",
    "DEFAULT_DATASET_ID",
    "calculate_rfm",
    "get_revenue_kpis",
    "get_revenue_trend",
    "get_revenue_by_country",
    "get_top_customers",
    "segment_customers",
    "compare_segments",
    "get_product_rankings",
    "get_lowest_performing_products",
    "run_market_basket_analysis",
    "assess_predictive_eligibility",
    "predict_customer_recurrence_and_clv",
    "ask_assistant",
    "AssistantResponse",
    "TOOL_REGISTRY",
    "generate_business_insights",
    "BusinessInsight",
    "generate_executive_brief_markdown",
    "export_customer_segments_csv",
]
