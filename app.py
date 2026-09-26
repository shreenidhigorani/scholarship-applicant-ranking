import streamlit as st
import pandas as pd
from pathlib import Path

from backend.db import (
    clear_applicants,
    insert_applicant,
    get_all_applicants,
    save_cluster_decision
)

from backend.similarity import calculate_similarity
from backend.union_find import UnionFind


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Scholarship Applicant System",
    page_icon="🎓",
    layout="wide"
)


# ---------------- LOAD CUSTOM CSS ----------------

css_file = Path(__file__).parent / "style.css"

with open(css_file, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# ---------------- HEADER ----------------

st.markdown("""
<div class="main-header">
    <h1>🎓 Scholarship Applicant System</h1>
    <p>
        A two-stage system for detecting duplicate applicants
        and supporting merit-based ranking.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("### Upload data")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV containing applicant information."
    )

    # Show detection settings only after CSV upload
    if uploaded_file is not None:

        st.markdown("### Detection settings")

        threshold = st.slider(
            "Similarity threshold",
            min_value=0,
            max_value=100,
            value=80,
            help=(
                "A higher value means records must be more similar "
                "before they are grouped together."
            )
        )

        st.caption(
            "Records with a similarity score at or above this "
            "threshold will be connected."
        )

        run_button = st.button(
            "🔍 Find Suspected Duplicates",
            type="primary",
            use_container_width=True
        )

    else:

        threshold = 0
        run_button = False


# ---------------- REQUIRED COLUMNS ----------------

required_columns = [
    "name",
    "address",
    "phone",
    "marks",
    "category_priority",
    "income_bracket",
    "distance_km"
]


# ---------------- INTRODUCTION ----------------

if uploaded_file is None:

    st.markdown(
        '<div class="section-title">Applicant Duplicate Checker</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Upload applicant records from the sidebar to identify "
        "potentially duplicated applications before the "
        "merit-ranking stage."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="info-card">
            <h3>📄 Upload</h3>
            <p>Upload applicant records in CSV format.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="info-card">
            <h3>🔍 Detect</h3>
            <p>Compare applicant records using similarity measures.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="info-card">
            <h3>✓ Review</h3>
            <p>Review suspected duplicate groups before ranking.</p>
        </div>
        """, unsafe_allow_html=True)


# ---------------- PROCESS UPLOADED FILE ----------------

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    with st.expander("Preview uploaded data", expanded=False):

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        st.error(
            "The following required columns are missing: "
            + ", ".join(missing_columns)
        )

    elif run_button:

        with st.spinner(
            "Running similarity checks and building clusters..."
        ):

            clear_applicants()

            for _, row in df.iterrows():

                insert_applicant(
                    row["name"],
                    row["address"],
                    row["phone"],
                    float(row["marks"]),
                    int(row["category_priority"]),
                    int(row["income_bracket"]),
                    float(row["distance_km"])
                )

            database_records = get_all_applicants()

            applicants = {}

            for record in database_records:

                applicant_id = record[0]

                applicants[applicant_id] = {
                    "id": record[0],
                    "name": record[1],
                    "address": record[2],
                    "phone": record[3],
                    "marks": record[4],
                    "category_priority": record[5],
                    "income_bracket": record[6],
                    "distance_km": record[7]
                }

            applicant_ids = list(applicants.keys())

            uf = UnionFind(applicant_ids)

            pair_scores = {}

            ids = applicant_ids

            for i in range(len(ids)):

                for j in range(i + 1, len(ids)):

                    id1 = ids[i]
                    id2 = ids[j]

                    applicant1 = applicants[id1]
                    applicant2 = applicants[id2]

                    score = calculate_similarity(
                        applicant1,
                        applicant2
                    )

                    pair_scores[(id1, id2)] = score

                    if score >= threshold:

                        uf.union(id1, id2)

            all_clusters = uf.get_clusters()

            duplicate_clusters = {}

            for cluster_id, members in all_clusters.items():

                if len(members) > 1:

                    duplicate_clusters[cluster_id] = members

            st.session_state["applicants"] = applicants
            st.session_state["duplicate_clusters"] = duplicate_clusters
            st.session_state["pair_scores"] = pair_scores
            st.session_state["decisions"] = {}
            st.session_state["total_uploaded"] = len(applicant_ids)

        st.success("Duplicate checking completed.")


# ---------------- HELPER FUNCTION ----------------

def cluster_average_score(members, pair_scores):

    scores = []

    for i in range(len(members)):

        for j in range(i + 1, len(members)):

            key = (members[i], members[j])

            if key not in pair_scores:

                key = (members[j], members[i])

            if key in pair_scores:

                scores.append(pair_scores[key])

    if not scores:

        return None

    return sum(scores) / len(scores)


# ---------------- RESULTS ----------------

if "duplicate_clusters" in st.session_state:

    duplicate_clusters = st.session_state["duplicate_clusters"]
    applicants = st.session_state["applicants"]
    pair_scores = st.session_state["pair_scores"]
    total_uploaded = st.session_state["total_uploaded"]
    decisions = st.session_state["decisions"]

    st.markdown(
        '<div class="section-title">Duplicate Detection Results</div>',
        unsafe_allow_html=True
    )

    confirmed_duplicate = sum(
        1
        for decision in decisions.values()
        if decision == "duplicate"
    )

    confirmed_distinct = sum(
        1
        for decision in decisions.values()
        if decision == "distinct"
    )

    pending = (
        len(duplicate_clusters)
        - confirmed_duplicate
        - confirmed_distinct
    )

    m1, m2, m3, m4 = st.columns(4)

    metric_data = [
        (m1, total_uploaded, "Applicants uploaded"),
        (m2, len(duplicate_clusters), "Clusters found"),
        (m3, pending, "Pending review"),
        (m4, confirmed_duplicate, "Confirmed duplicate")
    ]

    for col, value, label in metric_data:

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    if len(duplicate_clusters) == 0:

        st.success(
            "✓ No suspected duplicate clusters were found."
        )

    else:

        tab_all, tab_pending, tab_resolved = st.tabs(
            [
                "All clusters",
                "Pending review",
                "Resolved"
            ]
        )

        # ---------------- RENDER CLUSTER ----------------

        def render_cluster(
            cluster_number,
            cluster_id,
            members,
            tab_name
        ):

            avg_score = cluster_average_score(
                members,
                pair_scores
            )

            score_text = ""

            if avg_score is not None:

                score_text = (
                    f'<span class="score-pill">'
                    f'Avg similarity: {avg_score:.0f}%'
                    f'</span>'
                )

            st.markdown(
                f"""
                <div class="cluster-card">
                    <h3>Cluster {cluster_number}</h3>
                    <p>
                        {len(members)}
                        records connected by the similarity rule.
                    </p>
                    {score_text}
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(
                "View records in this cluster"
            ):

                cluster_data = []

                for applicant_id in members:

                    applicant = applicants[applicant_id]

                    cluster_data.append({
                        "ID": applicant["id"],
                        "Name": applicant["name"],
                        "Address": applicant["address"],
                        "Phone": applicant["phone"],
                        "Marks": applicant["marks"],
                        "Category Priority":
                            applicant["category_priority"],
                        "Income Bracket":
                            applicant["income_bracket"],
                        "Distance (km)":
                            applicant["distance_km"]
                    })

                cluster_df = pd.DataFrame(
                    cluster_data
                )

                st.dataframe(
                    cluster_df,
                    use_container_width=True,
                    hide_index=True
                )

            col1, col2 = st.columns(2)

            # ---------------- DUPLICATE BUTTON ----------------

            with col1:

                if st.button(
                    "✓ Confirm as Duplicate",
                    key=f"duplicate_{tab_name}_{cluster_id}",
                    use_container_width=True
                ):

                    st.session_state["decisions"][
                        cluster_id
                    ] = "duplicate"

                    save_cluster_decision(
                        cluster_id,
                        "duplicate"
                    )

                    st.rerun()

            # ---------------- DISTINCT BUTTON ----------------

            with col2:

                if st.button(
                    "✕ Mark as Distinct",
                    key=f"distinct_{tab_name}_{cluster_id}",
                    use_container_width=True
                ):

                    st.session_state["decisions"][
                        cluster_id
                    ] = "distinct"

                    save_cluster_decision(
                        cluster_id,
                        "distinct"
                    )

                    st.rerun()

            # ---------------- STATUS ----------------

            if cluster_id in decisions:

                decision = decisions[cluster_id]

                if decision == "duplicate":

                    st.markdown(
                        '<span class="status-pill-duplicate">'
                        'Confirmed duplicate'
                        '</span>',
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        '<span class="status-pill-distinct">'
                        'Marked distinct'
                        '</span>',
                        unsafe_allow_html=True
                    )

            else:

                st.markdown(
                    '<span class="status-pill-pending">'
                    'Pending review'
                    '</span>',
                    unsafe_allow_html=True
                )

            st.write("")

        # ---------------- CLUSTER LIST ----------------

        cluster_items = list(
            duplicate_clusters.items()
        )

        # ---------------- ALL CLUSTERS ----------------

        with tab_all:

            for idx, (cluster_id, members) in enumerate(
                cluster_items,
                start=1
            ):

                render_cluster(
                    idx,
                    cluster_id,
                    members,
                    "all"
                )

        # ---------------- PENDING CLUSTERS ----------------

        with tab_pending:

            any_pending = False

            for idx, (cluster_id, members) in enumerate(
                cluster_items,
                start=1
            ):

                if cluster_id not in decisions:

                    any_pending = True

                    render_cluster(
                        idx,
                        cluster_id,
                        members,
                        "pending"
                    )

            if not any_pending:

                st.info(
                    "No clusters left to review."
                )

        # ---------------- RESOLVED CLUSTERS ----------------

        with tab_resolved:

            any_resolved = False

            for idx, (cluster_id, members) in enumerate(
                cluster_items,
                start=1
            ):

                if cluster_id in decisions:

                    any_resolved = True

                    render_cluster(
                        idx,
                        cluster_id,
                        members,
                        "resolved"
                    )

            if not any_resolved:

                st.info(
                    "No clusters resolved yet."
                )

        # ---------------- DOWNLOAD DECISIONS ----------------

        if decisions:

            rows = []

            for cluster_id, members in duplicate_clusters.items():

                decision = decisions.get(
                    cluster_id,
                    "pending"
                )

                for applicant_id in members:

                    rows.append({
                        "cluster_id": cluster_id,
                        "applicant_id": applicant_id,
                        "name": applicants[applicant_id]["name"],
                        "decision": decision
                    })

            decisions_df = pd.DataFrame(rows)

            st.download_button(
                "⬇ Download decisions as CSV",
                data=decisions_df.to_csv(index=False),
                file_name="cluster_decisions.csv",
                mime="text/csv",
                use_container_width=True
            )


# ---------------- FOOTER ----------------

st.markdown("""
<div class="footer">
    Scholarship Applicant System • Discrete Mathematics Project
</div>
""", unsafe_allow_html=True)
