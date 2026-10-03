def dominates(applicant1, applicant2):
    """
    Checks whether applicant1 is at least as preferable
    as applicant2 according to all ranking criteria.
    """

    marks_condition = (
        applicant1["marks"] >= applicant2["marks"]
    )

    category_condition = (
        applicant1["category_priority"]
        <= applicant2["category_priority"]
    )

    income_condition = (
        applicant1["income_bracket"]
        <= applicant2["income_bracket"]
    )

    distance_condition = (
        applicant1["distance_km"]
        <= applicant2["distance_km"]
    )

    return (
        marks_condition
        and category_condition
        and income_condition
        and distance_condition
    )


def strictly_dominates(applicant1, applicant2):
    """
    Checks whether applicant1 is better than applicant2
    in at least one criterion and not worse in any criterion.
    """

    if not dominates(applicant1, applicant2):
        return False

    marks_better = (
        applicant1["marks"] > applicant2["marks"]
    )

    category_better = (
        applicant1["category_priority"]
        < applicant2["category_priority"]
    )

    income_better = (
        applicant1["income_bracket"]
        < applicant2["income_bracket"]
    )

    distance_better = (
        applicant1["distance_km"]
        < applicant2["distance_km"]
    )

    return (
        marks_better
        or category_better
        or income_better
        or distance_better
    )
