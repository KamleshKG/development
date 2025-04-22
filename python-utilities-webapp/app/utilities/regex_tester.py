import re

def test_regex(pattern, text, flags=0):
    """Test regular expression against text"""
    try:
        matches = list(re.finditer(pattern, text, flags))
        groups = []
        for match in matches:
            groups.append({
                "full_match": match.group(0),
                "groups": match.groups(),
                "span": match.span()
            })
        return {
            "valid": True,
            "matches": groups,
            "match_count": len(matches)
        }
    except re.error as e:
        return {"valid": False, "error": str(e)}

# Test Example:
if __name__ == "__main__":
    result = test_regex(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Contact us at support@example.com or sales@company.org"
    )
    print("Regex Matches:", result)