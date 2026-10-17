
"""Research quality, consistency, and evidence traceability dashboard."""

from pathlib import Path
import platform

import pandas as pd
import plotly.express as px
import sklearn
import streamlit as st

from customerinsight.dashboard_audit import (
    run_consistency_checks,
    run_research_audit,
)
from customerinsight.research_evidence import (
    RESEARCH_QUESTIONS,
    get_evidence_status,
)


ROOT = Path(__file__).resolve().parents[2]


def explanation(what, result, value, limitation):
    """Explain the evidence in everyday language."""

    with st.container(border=True):
        st.markdown("**What are we checking?**")
        st.write(what)

        st.markdown("**What did we find?**")
        st.write(result)

        st.markdown("**Why does it matter?**")
        st.write(value)

        with st.expander("Limitations"):
            st.write(limitation)


def show_integrity(audit):
    """Present the basic data integrity audit."""

    st.subheader("Dataset & Research Integrity")

    st.write(
        "Before trusting a visualization, we check that its "
        "underlying research file is available and structurally valid."
    )

    statuses = (
        audit["Status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Components")
    )

    left, right = st.columns([1, 1.8])

    with left:
        fig = px.bar(
            statuses,
            x="Status",
            y="Components",
            color="Status",
            text_auto=True,
            title="Research component status",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with right:
        st.dataframe(
            audit,
            hide_index=True,
            width="stretch",
        )

    ready = int((audit["Status"] == "Ready").sum())

    explanation(
        "We verify file availability, required columns, "
        "and selected numeric constraints.",
        f"{ready} of {len(audit)} research components passed "
        "the implemented basic checks.",
        "This helps detect missing data and malformed results "
        "before those results are presented to dashboard users.",
        "The Excel source is checked for existence only. "
        "Basic validation does not prove experiment accuracy.",
    )


def show_consistency(checks):
    """Display agreement between related research files."""

    st.subheader("Cross-File Consistency")

    st.write(
        "Individual files can be valid but still contradict "
        "one another. These checks compare related results."
    )

    passed = int((checks["Status"] == "Passed").sum())
    failed = int((checks["Status"] == "Failed").sum())
    skipped = int((checks["Status"] == "Not checked").sum())

    a, b, c = st.columns(3)
    a.metric("Passed checks", passed)
    b.metric("Failed checks", failed)
    c.metric("Not checked", skipped)

    st.dataframe(
        checks,
        hide_index=True,
        width="stretch",
    )

    with st.expander("Understand each consistency check", expanded=True):
        st.markdown(
            """
            **Customer coverage:** Do all cluster profile counts
            add up to the RFM customer population?

            **Stability statistics:** Can the reported mean,
            standard deviation, minimum and maximum be
            reproduced from individual ARI runs?

            **Run identifiers:** Is each experiment/run
            combination unique?

            **Validation configurations:** Was each
            preprocessing/K combination recorded once?
            """
        )

    if failed:
        st.error(
            "Some saved research results disagree. "
            "Investigate before using them in the scientific report."
        )
    elif skipped:
        st.warning(
            "Some consistency checks could not run. "
            "Inspect the Details column."
        )
    else:
        st.success("All implemented cross-file checks passed.")

    explanation(
        "We compare related research outputs instead "
        "of only inspecting their structure.",
        f"{passed} passed, {failed} failed, "
        f"and {skipped} could not be checked.",
        "Reconciliation helps detect omitted customers, "
        "inconsistent summaries and duplicate experiments.",
        "These checks do not establish correct clustering, "
        "external generalization or business usefulness.",
    )


def show_evidence_map():
    """Connect each research question with supporting project files."""

    st.subheader("Research Evidence Map")

    st.write(
        "Choose a research question to see how it connects "
        "to our methods, code, notebook, saved results and limitations."
    )

    options = {
        f"{question['id']} — {question['title']}": question
        for question in RESEARCH_QUESTIONS
    }

    selected = st.selectbox(
        "Research question",
        list(options),
    )
    question = options[selected]
    status = get_evidence_status(question, ROOT)

    st.markdown(f"### {question['question']}")
    st.write(f"**Method:** {question['method']}")

    st.progress(
        status["available"] / status["total"],
        text=(
            f"{status['available']} of "
            f"{status['total']} referenced files found"
        ),
    )

    st.markdown("#### Evidence trail")

    items = [
        ("Research question", question["question"]),
        ("Method", question["method"]),
        ("Implementation", ", ".join(question["implementation"])),
        ("Notebook", question["notebook"]),
        ("Experiment evidence", ", ".join(question["evidence"])),
        ("Documentation", question["documentation"]),
        ("Limitation", question["limitation"]),
    ]

    for title, detail in items:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(detail)

    if status["missing"]:
        st.warning(
            "Some referenced files are missing: "
            + ", ".join(status["missing"])
        )
    else:
        st.success("All referenced evidence files were found.")

    st.caption(
        "This map verifies file references, not the correctness "
        "of their contents or conclusions."
    )


def show_reproducibility(audit, checks):
    """Explain the environment and what remains to be verified."""

    st.subheader("Reproducibility & Research Transparency")

    st.write(
        "Another researcher should be able to understand "
        "the inputs, recreate the experiments and compare results."
    )

    versions = pd.DataFrame([
        {"Component": "Python", "Version": platform.python_version()},
        {"Component": "Pandas", "Version": pd.__version__},
        {"Component": "scikit-learn", "Version": sklearn.__version__},
        {"Component": "Streamlit", "Version": st.__version__},
    ])

    st.markdown("#### Current Python environment")
    st.dataframe(versions, hide_index=True, width="stretch")

    st.markdown("#### Research reproduction commands")

    st.code(
        "python -m pytest -v\n"
        "python scripts/build_customer_features.py\n"
        "python -m streamlit run app/main.py",
        language="bash",
    )

    st.info(
        "The feature-building command regenerates a processed dataset. "
        "Ensure the original retail workbook is available first. "
        "Other experiments are documented in their respective notebooks."
    )

    st.markdown("#### Remaining verification activities")

    activities = [
        "Run the complete automated test suite",
        "Execute each notebook from a clean kernel",
        "Confirm that regenerated results match saved evidence",
        "Review all dashboard pages manually",
        "Complete the scientific manuscript and references",
        "Verify a fresh environment installation",
    ]

    for activity in activities:
        st.checkbox(
            activity,
            value=False,
            key=f"reproduction_{activity}",
            help="A manual tracking control; not proof that this check ran.",
        )

    st.caption(
        "These checkboxes are local interface controls. "
        "They are not a permanent or independently verified test record."
    )

    st.divider()
    st.markdown("#### Download research assurance results")

    st.download_button(
        "Download file integrity audit",
        audit.to_csv(index=False),
        file_name="research_integrity.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download consistency checks",
        checks.to_csv(index=False),
        file_name="research_consistency.csv",
        mime="text/csv",
    )


def main():
    """Render the full Research Quality Center."""

    st.title("Research Quality Center")
    st.caption("CUSTOMERINSIGHT AI / EVIDENCE & REPRODUCIBILITY")

    st.write(
        "Understand which research outputs are available, "
        "whether related results agree and how our "
        "findings connect to their original evidence."
    )

    audit = run_research_audit(ROOT)
    checks = run_consistency_checks(ROOT)

    ready = int((audit["Status"] == "Ready").sum())
    passed = int((checks["Status"] == "Passed").sum())
    missing = int((audit["Status"] == "Missing").sum())
    failed = int((checks["Status"] == "Failed").sum())

    cards = st.columns(4)
    cards[0].metric("Research files ready", f"{ready}/{len(audit)}")
    cards[1].metric("Consistency checks passed", f"{passed}/{len(checks)}")
    cards[2].metric("Missing research files", missing)
    cards[3].metric("Consistency failures", failed)

    st.divider()

    integrity, consistency, evidence, reproducibility = st.tabs([
        "Data Integrity",
        "Consistency Checks",
        "Evidence Map",
        "Reproducibility",
    ])

    with integrity:
        show_integrity(audit)

    with consistency:
        show_consistency(checks)

    with evidence:
        show_evidence_map()

    with reproducibility:
        show_reproducibility(audit, checks)


main()
