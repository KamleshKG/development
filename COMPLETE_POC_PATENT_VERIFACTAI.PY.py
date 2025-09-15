# verifactai_poc.py
class VeriFactAIPOC:
    def __init__(self):
        # Internal Knowledge Graph (No external APIs)
        self.kg = {
            "eiffel_tower": {
                "location": "Paris",
                "height": 330,
                "built": 1889,
                "designer": "Gustave Eiffel"
            },
            "statue_of_liberty": {
                "location": "New York",
                "height": 93,
                "gifted": 1886
            }
        }

        # Resolution Rules Database
        self.correction_rules = {
            "geographic": {
                "pattern": r"in (\w+)",
                "action": "replace"
            },
            "temporal": {
                "pattern": r"in (\d{4})",
                "action": "replace"
            },
            "statistical": {
                "pattern": r"(\d+)\s*(meters|m|feet|ft)",
                "action": "correct_number"
            }
        }

    def diagnose(self, claim):
        """The core diagnostic engine."""
        results = []
        for entity, facts in self.kg.items():
            if entity in claim.lower():
                for fact, value in facts.items():
                    if fact == "location" and str(value) not in claim:
                        results.append(("geographic", value, f"Should be: {value}"))
                    if fact == "built" and str(value) not in claim:
                        results.append(("temporal", value, f"Built in: {value}"))
                    if fact == "height":
                        num = self.extract_number(claim)
                        if num and abs(num - value) > value * 0.1:  # 10% tolerance
                            results.append(("statistical", value, f"True height: {value}m"))
        return results

    def resolve(self, claim, diagnosis):
        """The resolution engine."""
        if not diagnosis:
            return claim

        error_type, correct_value, message = diagnosis[0]

        # Apply correction rules
        if error_type == "geographic":
            # Extract wrong city and replace
            wrong_place = self.extract_pattern(claim, r"in (\w+)")
            if wrong_place:
                return claim.replace(wrong_place, str(correct_value))

        elif error_type == "temporal":
            wrong_year = self.extract_pattern(claim, r"in (\d{4})")
            if wrong_year:
                return claim.replace(wrong_year, str(correct_value))

        elif error_type == "statistical":
            wrong_number = self.extract_number(claim)
            if wrong_number:
                return claim.replace(str(wrong_number), str(correct_value))

        return f"{claim} // CORRECTION: {message}"

    def extract_number(self, text):
        # Helper to extract numbers
        import re
        nums = re.findall(r'\d+', text)
        return int(nums[0]) if nums else None

    def extract_pattern(self, text, pattern):
        # Helper to extract regex pattern
        import re
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def analyze(self, llm_output):
        """End-to-end analysis."""
        print(f"Input: {llm_output}")

        # Step 1: Diagnose
        diagnosis = self.diagnose(llm_output)
        print(f"Diagnosis: {diagnosis[0] if diagnosis else 'No errors'}")

        # Step 2: Resolve
        if diagnosis:
            corrected = self.resolve(llm_output, diagnosis)
            print(f"Corrected: {corrected}")

            # Step 3: Self-heal (add to KG if new valid fact)
            self.self_heal(diagnosis)

        return corrected if diagnosis else llm_output

    def self_heal(self, diagnosis):
        """Simulate adding new knowledge to KG."""
        error_type, correct_value, message = diagnosis[0]
        # In real implementation, would add to KG here
        print(f"Self-Healing: Logging '{correct_value}' as verified truth\n")


# Run the POC
if __name__ == "__main__":
    verifact = VeriFactAIPOC()

    test_cases = [
        "The Eiffel Tower is in London",
        "The Eiffel Tower was built in 1995",
        "The Eiffel Tower is 500 meters tall"
    ]

    for test in test_cases:
        verifact.analyze(test)