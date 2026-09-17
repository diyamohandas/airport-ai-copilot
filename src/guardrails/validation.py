import re


VALID_AIRPORTS = {"SFO", "LAX", "JFK"}

MAX_QUERY_LENGTH = 500


def validate_query(query):
    """
    Validate a user query before it reaches the agent workflow.
    """

    errors = []

    if not isinstance(query, str):
        errors.append("Query must be a string.")

        return {
            "valid": False,
            "errors": errors,
            "sanitized_query": None,
        }

    query = query.strip()

    if not query:
        errors.append("Query cannot be empty.")

    if len(query) > MAX_QUERY_LENGTH:
        errors.append(
            f"Query cannot exceed {MAX_QUERY_LENGTH} characters."
        )

    # Basic control-character check.
    if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", query):
        errors.append(
            "Query contains invalid control characters."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "sanitized_query": query if not errors else None,
    }


def validate_airport_code(airport_code):
    """
    Validate an airport code.
    """

    if not isinstance(airport_code, str):
        return {
            "valid": False,
            "error": "Airport code must be a string.",
        }

    airport_code = airport_code.strip().upper()

    if airport_code not in VALID_AIRPORTS:
        return {
            "valid": False,
            "error": (
                f"Unsupported airport '{airport_code}'. "
                "Allowed airports are SFO, LAX, and JFK."
            ),
        }

    return {
        "valid": True,
        "airport_code": airport_code,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("INPUT VALIDATION TEST")
    print("=" * 70)

    tests = [
        "What is happening at SFO?",
        "",
        "Can we increase surge at LAX?",
        "A" * 501,
    ]

    for query in tests:

        result = validate_query(query)

        print("\nQuery:", repr(query))
        print(result)

    print("\nAirport validation:")

    for airport in ["SFO", "LAX", "JFK", "ABC"]:

        result = validate_airport_code(airport)

        print(airport, "->", result)

    print("=" * 70)
    print("INPUT VALIDATION TEST COMPLETED")
    print("=" * 70)
