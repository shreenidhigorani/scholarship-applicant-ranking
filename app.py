import streamlit as st
import pandas as pd
from pathlib import Path
from backend.db import (
    create_tables,
    clear_applicants,
    insert_applicant,
    get_all_applicants,
    save_cluster_decision
)
from backend.similarity import calculate_similarity
from backend.union_find import UnionFind
from backend.relation_checker import strictly_dominates
from backend.topo_sort import topological_sort
# =============================================================
# PAGE SETTINGS
# =============================================================
st.set_page_config(
    page_title="Meridian",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =============================================================
# CREATE DATABASE TABLES
# =============================================================
create_tables()
# =============================================================
# LOAD CUSTOM CSS
# =============================================================
css_file = Path(__file__).parent / "style.css"
with open(css_file, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )
# =============================================================
# APP STATE
# =============================================================
if "started" not in st.session_state:
    st.session_state["started"] = False
# =============================================================
# APP BAR
# =============================================================
if st.session_state["started"]:
    st.markdown("""
    <div class="app-bar">
        <div class="app-bar-logo">M</div>
        <div class="app-bar-brand">
            <span class="app-bar-name">Meridian</span>
            <span class="app-bar-tagline">
                Duplicate detection &amp; merit ranking
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
# =============================================================
# MERIDIAN HOME PAGE
# =============================================================
if not st.session_state["started"]:
    st.markdown("""
    <div class="hero">
        <div class="hero-logo">M</div>
        <div class="hero-name">MERIDIAN</div>
        <div class="hero-description">
            A structured system for identifying duplicate applications
            and generating a merit-based ordering.
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ---------------------------------------------------------
    # HOME PAGE CARDS
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="home-card">
            <div class="home-number">
                01
            </div>
            <h3>
                Identify
            </h3>
            <p>
                Detect potentially duplicated applicant records
                using similarity and equivalence classes.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="home-card">
            <div class="home-number">
                02
            </div>
            <h3>
                Compare
            </h3>
            <p>
                Compare applicants using a multi-criteria
                partial-order relation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="home-card">
            <div class="home-number">
                03
            </div>
            <h3>
                Rank
            </h3>
            <p>
                Generate an ordering that respects the
                preference relationships between applicants.
            </p>
        </div>
        """, unsafe_allow_html=True)
    # ---------------------------------------------------------
    # START BUTTON
    # ---------------------------------------------------------
    st.write("")
    start_col1, start_col2, start_col3 = st.columns(
        [1, 1, 1]
    )
    with start_col2:
        if st.button(
            "Begin Evaluation  →",
            type="primary",
            use_container_width=True
        ):
            st.session_state["started"] = True
            st.rerun()
    # ---------------------------------------------------------
    # HOME PAGE FOOTER
    # ---------------------------------------------------------
    st.markdown("""
    <div class="home-footer">
        Discrete mathematics applied to scholarship evaluation
    </div>
    """, unsafe_allow_html=True)
    # Stop here so the actual application does not
    # appear underneath the homepage.
    st.stop()
# =============================================================
# REQUIRED COLUMNS
# =============================================================
required_columns = [
    "name",
    "address",
    "phone",
    "marks",
    "category_priority",
    "income_bracket",
    "distance_km"
]
# =============================================================
# SAMPLE CSV
# =============================================================
_SAMPLE_CSV = (
    "name,address,phone,marks,category_priority,"
    "income_bracket,distance_km\n"
    "Alice Kumar,12 MG Road Bengaluru,9876543210,"
    "85.5,1,2,12.3\n"
    "Bob Sharma,45 Anna Nagar Chennai,9123456789,"
    "78.0,2,3,8.7\n"
    "Carol Nair,7 Park Street Kolkata,9988776655,"
    "92.0,1,1,5.0\n"
)
# =============================================================
# UPLOAD & SETTINGS CARD
# =============================================================
st.markdown("""
<div class="upload-card">
    <div class="upload-card-title">
        📂 Load Applicant Data
    </div>
</div>
""", unsafe_allow_html=True)
with st.container():
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV containing applicant information."
    )
    if uploaded_file is not None:
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
# =============================================================
# INTRODUCTION
# =============================================================
if uploaded_file is None:
    st.markdown(
        '<div class="section-title">Applicant Duplicate Checker</div>',
        unsafe_allow_html=True
    )
    st.write(
        "Upload applicant records above to identify "
        "potentially duplicated applications before the "
        "merit-ranking stage."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>📄 Upload</h3>
            <p>
                Upload applicant records in CSV format.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🔍 Detect</h3>
            <p>
                Compare applicant records using similarity measures.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>✓ Review</h3>
            <p>
                Review suspected duplicate groups before ranking.
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.write("")
    _dl_col, _ = st.columns([1, 2])
    with _dl_col:
        st.download_button(
            "⬇ Download sample CSV",
            data=_SAMPLE_CSV,
            file_name="sample_applicants.csv",
            mime="text/csv"
        )
    st.caption(
        "Use the sample file above to try the app with demo data."
    )
# =============================================================
# PROCESS UPLOADED FILE
# =============================================================
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander(
        "Preview uploaded data",
        expanded=False
    ):
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
            # -------------------------------------------------
            # INSERT APPLICANTS INTO DATABASE
            # -------------------------------------------------
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
            # -------------------------------------------------
            # GET APPLICANTS FROM DATABASE
            # -------------------------------------------------
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
            # -------------------------------------------------
            # UNION-FIND
            # -------------------------------------------------
            applicant_ids = list(applicants.keys())
            uf = UnionFind(applicant_ids)
            pair_scores = {}
            ids = applicant_ids
            # Compare every pair of applicants
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    id1 = ids[i]
                    id2 = ids[j]
                    applicant1 = applicants[id1]
                    applicant2 = applicants[id2]
                    # Calculate similarity
                    score = calculate_similarity(
                        applicant1,
                        applicant2
                    )
                    pair_scores[(id1, id2)] = score
                    # Connect records that meet threshold
                    if score >= threshold:
                        uf.union(
                            id1,
                            id2
                        )
            # -------------------------------------------------
            # GET CLUSTERS
            # -------------------------------------------------
            all_clusters = uf.get_clusters()
            duplicate_clusters = {}
            for cluster_id, members in all_clusters.items():
                if len(members) > 1:
                    duplicate_clusters[cluster_id] = members
            # -------------------------------------------------
            # STORE STAGE 1 DATA
            # -------------------------------------------------
            st.session_state["applicants"] = applicants
            st.session_state["duplicate_clusters"] = (
                duplicate_clusters
            )
            st.session_state["pair_scores"] = pair_scores
            st.session_state["decisions"] = {}
            st.session_state["total_uploaded"] = len(
                applicant_ids
            )
            # -------------------------------------------------
            # RESET STAGE 2
            # -------------------------------------------------
            st.session_state["ranking_applicants"] = {}
            st.session_state["stage2_ranking"] = None
            st.session_state["stage2_graph"] = {}
            st.session_state["stage2_comparisons"] = []
        st.success(
            "Duplicate checking completed."
        )
# =============================================================
# HELPER FUNCTION
# =============================================================


def cluster_average_score(
    members,
    pair_scores
):
    scores = []
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            key = (
                members[i],
                members[j]
            )
            if key not in pair_scores:
                key = (
                    members[j],
                    members[i]
                )
            if key in pair_scores:
                scores.append(
                    pair_scores[key]
                )
    if not scores:
        return None
    return sum(scores) / len(scores)


# =============================================================
# STAGE 1 — DUPLICATE DETECTION
# =============================================================
if "duplicate_clusters" in st.session_state:
    duplicate_clusters = (
        st.session_state["duplicate_clusters"]
    )
    applicants = (
        st.session_state["applicants"]
    )
    pair_scores = (
        st.session_state["pair_scores"]
    )
    total_uploaded = (
        st.session_state["total_uploaded"]
    )
    decisions = (
        st.session_state["decisions"]
    )
    st.markdown(
        '<div class="section-title">Duplicate Detection</div>',
        unsafe_allow_html=True
    )
    # ---------------------------------------------------------
    # DECISION COUNTS
    # ---------------------------------------------------------
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
    # ---------------------------------------------------------
    # METRIC CARDS
    # ---------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    metric_data = [
        (
            m1,
            total_uploaded,
            "Applicants uploaded"
        ),
        (
            m2,
            len(duplicate_clusters),
            "Clusters found"
        ),
        (
            m3,
            pending,
            "Pending review"
        ),
        (
            m4,
            confirmed_duplicate,
            "Confirmed duplicate"
        )
    ]
    for col, value, label in metric_data:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {value}
                    </div>
                    <div class="metric-label">
                        {label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.write("")
    # ---------------------------------------------------------
    # NO CLUSTERS
    # ---------------------------------------------------------
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
        # -----------------------------------------------------
        # RENDER CLUSTER
        # -----------------------------------------------------

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
                    <h3>
                        Cluster {cluster_number}
                    </h3>
                    <p>
                        {len(members)}
                        records connected by the similarity rule.
                    </p>
                    {score_text}
                </div>
                """,
                unsafe_allow_html=True
            )
            # -------------------------------------------------
            # CLUSTER RECORDS
            # -------------------------------------------------
            with st.expander(
                "View records in this cluster"
            ):
                cluster_data = []
                for applicant_id in members:
                    applicant = applicants[
                        applicant_id
                    ]
                    cluster_data.append({
                        "ID":
                            applicant["id"],
                        "Name":
                            applicant["name"],
                        "Address":
                            applicant["address"],
                        "Phone":
                            applicant["phone"],
                        "Marks":
                            applicant["marks"],
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
            # -------------------------------------------------
            # DECISION BUTTONS
            # -------------------------------------------------
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "✓ Confirm as Duplicate",
                    key=(
                        f"duplicate_"
                        f"{tab_name}_"
                        f"{cluster_id}"
                    ),
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
            with col2:
                if st.button(
                    "✕ Mark as Distinct",
                    key=(
                        f"distinct_"
                        f"{tab_name}_"
                        f"{cluster_id}"
                    ),
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
            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------
            if cluster_id in decisions:
                decision = decisions[
                    cluster_id
                ]
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
        # -----------------------------------------------------
        # CLUSTER LIST
        # -----------------------------------------------------
        cluster_items = list(
            duplicate_clusters.items()
        )
        # -----------------------------------------------------
        # ALL CLUSTERS
        # -----------------------------------------------------
        with tab_all:
            for idx, (
                cluster_id,
                members
            ) in enumerate(
                cluster_items,
                start=1
            ):
                render_cluster(
                    idx,
                    cluster_id,
                    members,
                    "all"
                )
        # -----------------------------------------------------
        # PENDING CLUSTERS
        # -----------------------------------------------------
        with tab_pending:
            any_pending = False
            for idx, (
                cluster_id,
                members
            ) in enumerate(
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
        # -----------------------------------------------------
        # RESOLVED CLUSTERS
        # -----------------------------------------------------
        with tab_resolved:
            any_resolved = False
            for idx, (
                cluster_id,
                members
            ) in enumerate(
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
        # -----------------------------------------------------
        # DOWNLOAD DECISIONS
        # -----------------------------------------------------
        if decisions:
            rows = []
            for cluster_id, members in (
                duplicate_clusters.items()
            ):
                decision = decisions.get(
                    cluster_id,
                    "pending"
                )
                for applicant_id in members:
                    rows.append({
                        "cluster_id":
                            cluster_id,
                        "applicant_id":
                            applicant_id,
                        "name":
                            applicants[
                                applicant_id
                            ]["name"],
                        "decision":
                            decision
                    })
            decisions_df = pd.DataFrame(
                rows
            )
            st.download_button(
                "⬇ Download decisions as CSV",
                data=decisions_df.to_csv(
                    index=False
                ),
                file_name="cluster_decisions.csv",
                mime="text/csv",
                use_container_width=True
            )
# =============================================================
# STAGE 2 — MERIT EVALUATION
# =============================================================
if "duplicate_clusters" in st.session_state:
    st.markdown(
        '<div class="section-title">Merit Evaluation</div>',
        unsafe_allow_html=True
    )
    duplicate_clusters = (
        st.session_state["duplicate_clusters"]
    )
    applicants = (
        st.session_state["applicants"]
    )
    decisions = (
        st.session_state["decisions"]
    )
    # ---------------------------------------------------------
    # CHECK FOR PENDING CLUSTERS
    # ---------------------------------------------------------
    pending_clusters = [
        cluster_id
        for cluster_id in duplicate_clusters
        if cluster_id not in decisions
    ]
    if pending_clusters:
        st.info(
            "Please review all suspected duplicate clusters "
            "before starting the merit evaluation."
        )
    else:
        # -----------------------------------------------------
        # BUILD RANKING APPLICANTS
        # -----------------------------------------------------
        duplicate_applicant_ids = set()
        for cluster_id, members in (
            duplicate_clusters.items()
        ):
            if decisions.get(
                cluster_id
            ) == "duplicate":
                members_sorted = sorted(
                    members
                )
                for applicant_id in (
                    members_sorted[1:]
                ):
                    duplicate_applicant_ids.add(
                        applicant_id
                    )
        ranking_applicants = {}
        for applicant_id, applicant in (
            applicants.items()
        ):
            if applicant_id not in (
                duplicate_applicant_ids
            ):
                ranking_applicants[
                    applicant_id
                ] = applicant
        # Keep applicants available after reruns
        st.session_state[
            "ranking_applicants"
        ] = ranking_applicants
        # -----------------------------------------------------
        # STAGE 2 METRIC CARDS
        # -----------------------------------------------------
        _comparisons_for_metrics = (
            st.session_state.get(
                "stage2_comparisons",
                []
            )
        )
        _eligible_count = len(
            ranking_applicants
        )
        _comparable_count = sum(
            1
            for _r in _comparisons_for_metrics
            if _r.get(
                "Result",
                ""
            ) != "Incomparable"
        )
        _incomparable_count = sum(
            1
            for _r in _comparisons_for_metrics
            if _r.get(
                "Result",
                ""
            ) == "Incomparable"
        )
        _s2m1, _s2m2, _s2m3 = st.columns(3)
        _s2_metrics = [
            (
                _s2m1,
                _eligible_count,
                "Eligible applicants"
            ),
            (
                _s2m2,
                _comparable_count,
                "Comparable pairs"
            ),
            (
                _s2m3,
                _incomparable_count,
                "Incomparable pairs"
            )
        ]
        for _col, _val, _lbl in _s2_metrics:
            with _col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">
                            {_val}
                        </div>
                        <div class="metric-label">
                            {_lbl}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.write("")
        # -----------------------------------------------------
        # ELIGIBLE APPLICANTS
        # -----------------------------------------------------
        st.markdown(
            "### 📋 Applicants Entering Merit Evaluation"
        )
        st.write(
            f"Applicants available for ranking: "
            f"**{len(ranking_applicants)}**"
        )
        eligible_data = []
        for display_id, (
            applicant_id,
            applicant
        ) in enumerate(
            ranking_applicants.items(),
            start=1
        ):
            eligible_data.append({
                "Applicant No.":
                    display_id,
                "Name":
                    applicant["name"],
                "Marks":
                    applicant["marks"],
                "Category Priority":
                    applicant[
                        "category_priority"
                    ],
                "Income Bracket":
                    applicant[
                        "income_bracket"
                    ],
                "Distance (km)":
                    applicant[
                        "distance_km"
                    ]
            })
        eligible_df = pd.DataFrame(
            eligible_data
        )
        st.dataframe(
            eligible_df,
            use_container_width=True,
            hide_index=True
        )
        # -----------------------------------------------------
        # NEED AT LEAST TWO APPLICANTS
        # -----------------------------------------------------
        if len(ranking_applicants) < 2:
            st.warning(
                "At least two applicants are required "
                "to create a merit evaluation."
            )
        else:
            # -------------------------------------------------
            # GENERATE MERIT EVALUATION
            # -------------------------------------------------
            evaluation_button = st.button(
                "Generate Merit Evaluation",
                type="primary",
                use_container_width=True
            )
            if evaluation_button:
                with st.spinner(
                    "Building Applicant Preference Analysis "
                    "and preference relations..."
                ):
                    graph = {}
                    applicant_ids = list(
                        ranking_applicants.keys()
                    )
                    # Create empty adjacency list
                    for applicant_id in applicant_ids:
                        graph[
                            applicant_id
                        ] = []
                    # -------------------------------------------------
                    # PAIRWISE COMPARISON
                    # -------------------------------------------------
                    comparison_rows = []
                    for i in range(
                        len(applicant_ids)
                    ):
                        for j in range(
                            i + 1,
                            len(applicant_ids)
                        ):
                            id1 = applicant_ids[i]
                            id2 = applicant_ids[j]
                            applicant1 = (
                                ranking_applicants[id1]
                            )
                            applicant2 = (
                                ranking_applicants[id2]
                            )
                            if strictly_dominates(
                                applicant1,
                                applicant2
                            ):
                                graph[id1].append(
                                    id2
                                )
                                result = (
                                    f"{applicant1['name']} "
                                    f"is preferred to "
                                    f"{applicant2['name']}"
                                )
                            elif strictly_dominates(
                                applicant2,
                                applicant1
                            ):
                                graph[id2].append(
                                    id1
                                )
                                result = (
                                    f"{applicant2['name']} "
                                    f"is preferred to "
                                    f"{applicant1['name']}"
                                )
                            else:
                                result = (
                                    "Incomparable"
                                )
                            comparison_rows.append({
                                "Applicant A":
                                    applicant1["name"],
                                "Applicant B":
                                    applicant2["name"],
                                "Result":
                                    result
                            })
                    st.session_state[
                        "stage2_graph"
                    ] = graph
                    st.session_state[
                        "stage2_comparisons"
                    ] = comparison_rows
                    st.session_state[
                        "stage2_ranking"
                    ] = None
                st.rerun()
            # -------------------------------------------------
            # SHOW RESULTS
            # -------------------------------------------------
            comparisons = (
                st.session_state.get(
                    "stage2_comparisons",
                    []
                )
            )
            graph = (
                st.session_state.get(
                    "stage2_graph",
                    {}
                )
            )
            if comparisons:
                # ---------------------------------------------
                # PAIRWISE COMPARISON TABLE
                # ---------------------------------------------
                st.markdown("---")
                st.markdown(
                    "### 1. Applicant Preference Analysis"
                )
                st.caption(
                    "Every pair of eligible applicants is "
                    "checked against all ranking criteria"
                )
                comparison_df = pd.DataFrame(
                    comparisons
                )
                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    hide_index=True
                )
                # ---------------------------------------------
                # PREFERENCE RELATIONS
                # ---------------------------------------------
                st.markdown(
                    "### 2. Preference Relations"
                )
                preference_rows = []
                for source_id, targets in (
                    graph.items()
                ):
                    source = ranking_applicants.get(
                        source_id
                    )
                    if source is None:
                        continue
                    for target_id in targets:
                        target = (
                            ranking_applicants.get(
                                target_id
                            )
                        )
                        if target is None:
                            continue
                        preference_rows.append({
                            "Preferring Applicant":
                                source["name"],
                            "Less Preferred Applicant":
                                target["name"],
                            "Relation":
                                "→"
                        })
                if preference_rows:
                    preference_df = pd.DataFrame(
                        preference_rows
                    )
                    st.dataframe(
                        preference_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No applicant strictly dominates another "
                        "under the current criteria. The applicants "
                        "are therefore incomparable."
                    )
                # ---------------------------------------------
                # PREFERENCE GRAPH
                # ---------------------------------------------
                st.markdown(
                    "### 3. Preference Graph"
                )
                st.caption(
                    "The directed graph shows the preference "
                    "relations between applicants. An arrow from "
                    "applicant A to applicant B indicates that "
                    "A is preferred over B."
                )
                dot = """
                digraph {
                    rankdir=LR;
                    bgcolor="#E9EEF6";
                    node [
                        shape=box,
                        style="filled,rounded",
                        fillcolor="#FFFFFF",
                        color="#1E3A8A",
                        fontcolor="#1F2937",
                        fontname="Inter",
                        penwidth=1.5
                    ];
                    edge [
                        color="#64748B",
                        penwidth=1.2,
                        arrowsize=0.8
                    ];
                """
                for applicant_id, applicant in (
                    ranking_applicants.items()
                ):
                    safe_name = (
                        str(applicant["name"])
                        .replace(
                            "\\",
                            "\\\\"
                        )
                        .replace(
                            '"',
                            '\\"'
                        )
                    )
                    dot += (
                        f'"{applicant_id}" '
                        f'[label="{safe_name}"];'
                    )
                for source_id, targets in graph.items():
                    for target_id in targets:
                        dot += (
                            f'"{source_id}" -> '
                            f'"{target_id}";'
                        )
                dot += "}"
                st.graphviz_chart(
                    dot,
                    use_container_width=True
                )
                st.caption(
                    "The preference graph is stored as an adjacency "
                    "list in Python. Graphviz is used only to display "
                    "the graph."
                )
                # ---------------------------------------------
                # FINAL RANKING
                # ---------------------------------------------
                st.markdown("---")
                final_button = st.button(
                    "Generate Final Merit Ranking 🏆",
                    type="primary",
                    use_container_width=True
                )
                if final_button:
                    ranking = topological_sort(
                        graph
                    )
                    if ranking is None:
                        st.session_state[
                            "stage2_ranking"
                        ] = None
                        st.error(
                            "A cycle was detected in the dominance "
                            "graph. A valid topological ranking could "
                            "not be created."
                        )
                    else:
                        st.session_state[
                            "stage2_ranking"
                        ] = ranking
                        st.rerun()
# =============================================================
# DISPLAY FINAL MERIT RANKING
# =============================================================
if st.session_state.get(
    "stage2_ranking"
) is not None:
    ranking = st.session_state[
        "stage2_ranking"
    ]
    ranking_applicants = (
        st.session_state.get(
            "ranking_applicants",
            {}
        )
    )
    st.markdown(
        '<div class="section-title">Final Merit Ranking</div>',
        unsafe_allow_html=True
    )
    st.caption(
        "The final order is obtained using topological sorting "
        "of the preference graph."
    )
    ranking_rows = []
    for position, applicant_id in enumerate(
        ranking,
        start=1
    ):
        applicant = ranking_applicants.get(
            applicant_id
        )
        if applicant is not None:
            ranking_rows.append({
                "Rank":
                    position,
                "Applicant":
                    applicant["name"],
                "Marks":
                    applicant["marks"],
                "Category Priority":
                    applicant[
                        "category_priority"
                    ],
                "Income Bracket":
                    applicant[
                        "income_bracket"
                    ],
                "Distance (km)":
                    applicant[
                        "distance_km"
                    ]
            })
    ranking_df = pd.DataFrame(
        ranking_rows
    )
    # ---------------------------------------------------------
    # HIGHLIGHT TOP 3
    # ---------------------------------------------------------

    def _highlight_top3(row):
        if row["Rank"] <= 3:
            return [
                "background-color: #EFF6FF; "
                "color: #1E3A8A; "
                "font-weight: 600;"
            ] * len(row)
        return [
            ""
        ] * len(row)
    _ranking_display = ranking_df.style.apply(
        _highlight_top3,
        axis=1
    )
    st.dataframe(
        _ranking_display,
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        "⬇ Download Merit Ranking",
        data=ranking_df.to_csv(
            index=False
        ),
        file_name="merit_ranking.csv",
        mime="text/csv",
        use_container_width=True
    )
# =============================================================
# FOOTER
# =============================================================
st.markdown("""
<div class="footer">
    Meridian &bull; Built by Shreenidhi Gorani
</div>
""", unsafe_allow_html=True)
