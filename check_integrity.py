import ast
import sys

src = open("app.py", encoding="utf-8").read()

try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)
    sys.exit(1)

checks = {
    "Meridian in src":          "Meridian" in src,
    "old name gone":             "Scholarship Applicant System" not in src,
    "footer updated":            "Built by Shreenidhi Gorani" in src,
    "step-indicator removed":    "step-indicator" not in src,
    "app-bar present":           "app-bar" in src,
    "DOT bgcolor updated":       'bgcolor="#E9EEF6"' in src,
    "create_tables":             "create_tables()" in src,
    "clear_applicants":          "clear_applicants()" in src,
    "get_all_applicants":        "get_all_applicants()" in src,
    "calculate_similarity":      "calculate_similarity" in src,
    "topological_sort":          "topological_sort" in src,
    "strictly_dominates":        "strictly_dominates" in src,
    "UnionFind":                 "UnionFind" in src,
    "read_csv":                  "df = pd.read_csv(uploaded_file)" in src,
    "threshold=0 fallback":      "threshold = 0" in src,
    "run_button=False fallback": "run_button = False" in src,
    "required_columns":          "required_columns = [" in src,
    "cluster_average_score":     "def cluster_average_score" in src,
    "ranking_df":                "ranking_df = pd.DataFrame(" in src,
    "ranking csv":               "ranking_df.to_csv(index=False)" in src,
    "decisions csv":             "decisions_df.to_csv(index=False)" in src,
    "rerun":                     "st.rerun()" in src,
}

failed = [k for k, v in checks.items() if not v]
if failed:
    print("FAILED:", failed)
    sys.exit(1)

print("ALL CHECKS PASSED")
