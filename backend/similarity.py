from rapidfuzz.fuzz import token_sort_ratio


def calculate_similarity(applicant1, applicant2):
    """
    Calculate the similarity between two applicant records.
    applicant1 and applicant2 are dictionaries containing:
    name, address, and phone.
    Returns a score between 0 and 100.
    """
    # Compare names using token_sort_ratio.
    # Example:
    # "Ravi Kumar" and "Kumar Ravi" will get a very high score.
    name_score = token_sort_ratio(
        applicant1["name"],
        applicant2["name"]
    )
    # Compare addresses using simple normalized string comparison.
    address1 = applicant1["address"].strip().lower()
    address2 = applicant2["address"].strip().lower()
    if address1 == address2:
        address_score = 100
    else:
        address_score = token_sort_ratio(address1, address2)
    # Compare phone numbers.
    # Remove spaces and other common formatting characters first.
    phone1 = (
        applicant1["phone"]
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    phone2 = (
        applicant2["phone"]
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if phone1 == phone2:
        phone_score = 100
    else:
        phone_score = 0
    # Combine the three scores.
    # Name is given the highest importance.
    combined_score = (
        0.50 * name_score
        + 0.30 * address_score
        + 0.20 * phone_score
    )
    return round(combined_score, 2)
