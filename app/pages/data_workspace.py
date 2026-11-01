"""Multi-dataset workspace for uploading, mapping, and managing transaction datasets."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


from pathlib import Path
import re

import pandas as pd
import streamlit as st

from dashboard_ui import (
    apply_styles, page_header, section_header,
    get_active_dataset_id, set_active_dataset_id,
)
from customerinsight.schema import (
    CANONICAL_FIELDS, detect_column_mappings,
    coerce_canonical_types, assess_capabilities,
)
from customerinsight.cleaning import audit_data_quality, clean_canonical_transactions
from customerinsight.datasets import (
    list_datasets, register_uploaded_dataset, delete_dataset,
)


def render_capability_badge(name: str, enabled: bool):
    icon = "✅" if enabled else "⚠️"
    bg = "var(--ci-soft)" if enabled else "rgba(224, 160, 75, 0.15)"
    color = "var(--ci-accent)" if enabled else "#CF9950"
    st.markdown(
        f"""<span style="display:inline-block; padding:.25rem .6rem; border-radius:100px;
        background:{bg}; color:{color}; font-size:.78rem; font-weight:600; margin-right:.4rem; margin-bottom:.4rem;">
            {icon} {name}
        </span>""",
        unsafe_allow_html=True,
    )


def main():
    apply_styles()
    page_header(
        "Workspace / Ingestion & Quality", "Data Workspace",
        "Upload customer transaction datasets, configure schema mappings, review cleaning audits, and manage active workspaces.",
        purpose="Connect custom CSV or Excel files, map them into canonical transaction records, and preview data quality before running analytics.",
        benefit="Allows any store or e-commerce merchant to run customer intelligence on their own data without code changes.",
        technical="Validates fields against canonical transaction schema, performs type coercion, generates SQLite registry records, and persists clean Parquet files for sub-second analytical aggregations.",
    )

    tab_manage, tab_upload = st.tabs(["📁 Registered Datasets", "📤 Ingest New Dataset"])

    with tab_manage:
        section_header("Available Workspaces", "Switch the active dataset or remove custom datasets.")
        datasets = list_datasets()
        active_id = get_active_dataset_id()

        for ds in datasets:
            ds_id = ds["dataset_id"]
            is_active = ds_id == active_id
            is_builtin = ds.get("is_builtin", False)

            with st.container(border=True):
                col_info, col_stats, col_action = st.columns([4, 4, 3])

                with col_info:
                    st.markdown(f"### {ds['display_name']}")
                    st.caption(f"ID: `{ds_id}` • File: `{ds['filename']}`")
                    if is_builtin:
                        st.markdown('<span class="ci-badge">Built-in Benchmark</span>', unsafe_allow_html=True)
                    if is_active:
                        st.markdown('<span class="ci-badge" style="background:#147D72; color:white;">● Active Workspace</span>', unsafe_allow_html=True)

                with col_stats:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Transactions", f"{ds['accepted_rows']:,}")
                    c2.metric("Customers", f"{ds['unique_customers']:,}")
                    c3.metric("Currency", ds.get("currency", "GBP"))

                with col_action:
                    st.write("")
                    if not is_active:
                        if st.button("Set as Active", key=f"activate_{ds_id}", use_container_width=True):
                            set_active_dataset_id(ds_id)
                            st.rerun()
                    else:
                        st.button("Currently Active", disabled=True, key=f"active_lbl_{ds_id}", use_container_width=True)

                    if not is_builtin:
                        if st.button("🗑️ Delete Dataset", key=f"del_{ds_id}", type="secondary", use_container_width=True):
                            delete_dataset(ds_id)
                            if is_active:
                                set_active_dataset_id("online_retail")
                            st.success(f"Deleted dataset '{ds['display_name']}'")
                            st.rerun()

                # Capabilities preview
                caps = ds.get("capabilities", {})
                if caps:
                    st.write("")
                    st.caption("Supported Analyses:")
                    cap_cols = st.columns(5)
                    cap_labels = [
                        ("RFM Segmentation", caps.get("rfm", False)),
                        ("Revenue Analytics", caps.get("revenue_kpis", False)),
                        ("Product Intelligence", caps.get("product_rankings", False)),
                        ("Market Basket Rules", caps.get("market_basket", False)),
                        ("Geographic Breakdown", caps.get("geo_breakdown", False)),
                    ]
                    for idx, (label, ok) in enumerate(cap_labels):
                        with cap_cols[idx]:
                            render_capability_badge(label, ok)

    with tab_upload:
        section_header("Upload Transaction File", "Upload a CSV or Excel export containing orders, line items, and customer IDs.")
        uploaded_file = st.file_uploader(
            "Select CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Files should contain transaction rows with customer, order, date, and spending details.",
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name
            clean_default_name = re.sub(r"[^\w\s-]", "", Path(file_name).stem).strip()

            try:
                with st.spinner("Reading uploaded file preview..."):
                    if file_name.endswith(".csv"):
                        df_raw = pd.read_csv(uploaded_file, nrows=10000)
                    else:
                        df_raw = pd.read_excel(uploaded_file, nrows=10000)
            except Exception as e:
                st.error(f"Error parsing uploaded file: {e}")
                return

            st.success(f"Successfully loaded preview of **{file_name}** ({len(df_raw):,} sample rows scanned, {len(df_raw.columns)} columns detected).")

            with st.expander("👀 Raw File Preview (First 5 Rows)", expanded=False):
                st.dataframe(df_raw.head(5), use_container_width=True)

            # Auto Column Detection
            detected_mappings = detect_column_mappings(df_raw)

            st.write("---")
            section_header("Schema Field Mapping", "Match your file columns to the canonical platform fields.")
            st.info("The platform auto-detected the best matching columns. You can manually adjust any mapping below.")

            available_cols = ["(None / Not present)"] + list(df_raw.columns)

            col_map_inputs = {}
            grid_cols = st.columns(2)

            fields_list = list(CANONICAL_FIELDS.items())
            for idx, (field_name, field_spec) in enumerate(fields_list):
                target_col = grid_cols[idx % 2]
                detected_col = detected_mappings.get(field_name)

                default_idx = 0
                if detected_col and detected_col in available_cols:
                    default_idx = available_cols.index(detected_col)

                required_marker = " *(Required)*" if field_spec["required"] else " *(Optional)*"
                with target_col:
                    chosen = st.selectbox(
                        f"**{field_spec['description']}** (`{field_name}`){required_marker}",
                        options=available_cols,
                        index=default_idx,
                        key=f"map_{field_name}",
                        help=f"Target type: {field_spec['type']}",
                    )
                    col_map_inputs[field_name] = None if chosen == "(None / Not present)" else chosen

            # Capability Assessment live preview
            caps_live = assess_capabilities(col_map_inputs)
            st.write("")
            st.markdown("**Analytic Capabilities with Selected Mappings:**")
            badge_cols = st.columns(5)
            badge_items = [
                ("RFM Segmentation", caps_live.get("rfm", False)),
                ("Revenue Analytics", caps_live.get("revenue_kpis", False)),
                ("Product Intelligence", caps_live.get("product_rankings", False)),
                ("Market Basket Rules", caps_live.get("market_basket", False)),
                ("Geographic Breakdown", caps_live.get("geo_breakdown", False)),
            ]
            for idx, (lbl, val) in enumerate(badge_items):
                with badge_cols[idx]:
                    render_capability_badge(lbl, val)

            # Data Cleaning Options
            st.write("---")
            section_header("Data Cleaning & Coercion Rules", "Configure how transaction records will be validated and scrubbed.")

            c_opt1, c_opt2 = st.columns(2)
            with c_opt1:
                display_name = st.text_input("Dataset Display Name", value=clean_default_name.title() or "Custom Dataset")
                currency_code = st.text_input("Default Currency Code (ISO)", value="GBP", max_chars=5).strip().upper()
                drop_missing_cust = st.checkbox("Drop rows with missing Customer ID", value=True)
                drop_negative_qty = st.checkbox("Drop negative / zero quantities (refunds/cancellations)", value=True)

            with c_opt2:
                drop_negative_price = st.checkbox("Drop negative / zero unit prices", value=True)
                drop_duplicates = st.checkbox("Deduplicate identical transaction rows", value=True)

            # Audit & Ingestion
            if st.button("🚀 Process, Clean & Register Dataset", type="primary", use_container_width=True):
                # Check required fields
                missing_reqs = [
                    f for f, spec in CANONICAL_FIELDS.items()
                    if spec["required"] and not col_map_inputs.get(f)
                ]
                if missing_reqs:
                    st.error(f"Cannot ingest dataset: Missing required canonical fields: {', '.join(missing_reqs)}")
                    return

                try:
                    with st.spinner("Processing complete file, applying schema coercion and cleaning rules..."):
                        # Read entire file
                        uploaded_file.seek(0)
                        if file_name.endswith(".csv"):
                            df_full = pd.read_csv(uploaded_file, low_memory=False)
                        else:
                            df_full = pd.read_excel(uploaded_file)

                        # Clean dataset and save
                        ds_meta = register_uploaded_dataset(
                            df_raw=df_full,
                            display_name=display_name,
                            filename=file_name,
                            column_mapping=col_map_inputs,
                            default_currency=currency_code or "GBP",
                            drop_missing_customers=drop_missing_cust,
                            drop_negative_quantities=drop_negative_qty,
                            drop_negative_prices=drop_negative_price,
                            drop_duplicates=drop_duplicates,
                        )

                        set_active_dataset_id(ds_meta["dataset_id"])
                        st.success(f"🎉 Dataset '{ds_meta['display_name']}' successfully ingested and set as the active workspace!")
                        st.rerun()

                except Exception as ex:
                    st.error(f"Failed to ingest dataset: {ex}")


if __name__ == "__main__":
    main()
