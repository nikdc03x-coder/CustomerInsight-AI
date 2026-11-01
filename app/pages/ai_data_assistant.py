"""Natural language AI Data Assistant backed by deterministic calculation tools."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


import pandas as pd
import streamlit as st

from dashboard_ui import (
    apply_styles, page_header, section_header,
    load_active_transactions, get_active_dataset_metadata,
    render_dataset_banner,
)
from customerinsight.ai_assistant import ask_assistant


def main():
    apply_styles()
    page_header(
        "AI & Strategy / Natural Language Analytics", "AI Data Assistant",
        "Ask questions about your transactions, customers, and products in plain English, answered strictly by live calculations.",
        purpose="Empower non-technical stakeholders to query customer and business metrics instantly without writing SQL or code.",
        benefit="Eliminates AI hallucinations by grounding every answer in deterministic analytical functions executed on the active dataset.",
        technical="Classifies intent and parameters using regex matching, routes to verified statistical tools in TOOL_REGISTRY, and formats responses with explicit calculation scope, currency symbols, and analytical caveats.",
    )

    render_dataset_banner()
    meta = get_active_dataset_metadata()
    dataset_name = meta.get("display_name", "Active Dataset")
    dataset_id = meta.get("dataset_id", "online_retail")
    currency = meta.get("currency", "GBP")

    try:
        df = load_active_transactions()
    except Exception as e:
        st.error(f"Could not load active dataset: {e}")
        return

    if df.empty:
        st.warning("Active dataset has no transaction records.")
        return

    # Initialize chat history
    if "assistant_messages" not in st.session_state:
        st.session_state["assistant_messages"] = [
            {
                "role": "assistant",
                "direct_answer": (
                    f"Hello! I am your AI Data Assistant for **{dataset_name}**. "
                    "I compute exact metrics directly from your transaction records. "
                    "What would you like to know about your revenue, top customers, or product baskets?"
                ),
                "supporting_metrics": {},
                "tabular_data": None,
                "period_analyzed": "",
                "limitations": "",
                "suggested_questions": [
                    "What is our total revenue and order count?",
                    "Who are my top 5 customers?",
                    "What is our average order value?",
                    "Which products are frequently bought together?",
                ],
            }
        ]

    # Quick prompt buttons
    st.markdown("**Suggested Quick Inquiries:**")
    prompt_cols = st.columns(4)
    quick_prompts = [
        "What is our total revenue and order count?",
        "Who are my top 5 customers?",
        "What is our average order value?",
        "Which products are frequently bought together?",
    ]

    selected_prompt = None
    for idx, prompt_text in enumerate(quick_prompts):
        with prompt_cols[idx]:
            if st.button(prompt_text, key=f"quick_btn_{idx}", use_container_width=True):
                selected_prompt = prompt_text

    st.write("---")

    # Render Chat History
    for msg in st.session_state["assistant_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["direct_answer"])

            # Supporting metrics
            metrics = msg.get("supporting_metrics") or {}
            if metrics:
                metric_cols = st.columns(len(metrics))
                for col_idx, (m_label, m_val) in enumerate(metrics.items()):
                    with metric_cols[col_idx]:
                        st.metric(m_label.replace("_", " ").title(), str(m_val))

            # Tabular data
            tbl = msg.get("tabular_data")
            if tbl:
                df_tbl = pd.DataFrame(tbl)
                with st.expander("📊 View Detailed Data Table", expanded=True):
                    st.dataframe(df_tbl, use_container_width=True, hide_index=True)

            # Metadata & caveats
            period = msg.get("period_analyzed")
            limits = msg.get("limitations")
            if period or limits:
                st.caption(f"📅 **Scope**: {period or 'All active records'}  |  ⚠️ **Caveat**: {limits or 'Strictly computed on verified sales'}")

    # Process Input
    user_query = st.chat_input("Ask a question about your revenue, customers, or products...") or selected_prompt

    if user_query:
        # Add user message to state
        st.session_state["assistant_messages"].append({
            "role": "user",
            "direct_answer": user_query,
            "supporting_metrics": {},
            "tabular_data": None,
            "period_analyzed": "",
            "limitations": "",
            "suggested_questions": [],
        })

        # Run assistant computation
        with st.spinner("Executing analytical query on dataset..."):
            res = ask_assistant(
                user_query,
                df=df,
                dataset_name=dataset_name,
                dataset_id=dataset_id,
                currency=currency,
            )

        # Append assistant response
        st.session_state["assistant_messages"].append({
            "role": "assistant",
            "direct_answer": res.direct_answer,
            "supporting_metrics": res.supporting_metrics,
            "tabular_data": res.tabular_data,
            "period_analyzed": res.period_analyzed,
            "limitations": res.limitations,
            "suggested_questions": res.suggested_follow_up_questions,
        })
        st.rerun()

    st.write("")
    if st.button("🧹 Clear Chat History", type="secondary"):
        st.session_state.pop("assistant_messages", None)
        st.rerun()


if __name__ == "__main__":
    main()
