# import yaml
# from yaml import YAMLError
#
#
# def validate_yaml(yaml_content):
#     """Validate YAML content and return errors if any"""
#     try:
#         yaml.safe_load(yaml_content)
#         return {"valid": True, "message": "Valid YAML"}
#     except YAMLError as e:
#         return {"valid": False, "message": str(e)}
#
#
# def format_yaml(yaml_content):
#     """Format ugly YAML into pretty version"""
#     try:
#         parsed = yaml.safe_load(yaml_content)
#         return {
#             "success": True,
#             "formatted": yaml.dump(parsed, sort_keys=False, indent=2)
#         }
#     except YAMLError as e:
#         return {"success": False, "error": str(e)}
#
#
# # Test Example:
# if __name__ == "__main__":
#     test_yaml = """
#     name: John Doe
#     age: 30
#     skills:
#       - Python
#       - YAML    # Bad indentation
#     """
#
#     print("Validation Result:", validate_yaml(test_yaml))
#     print("Formatted YAML:", format_yaml(test_yaml)["formatted"])

import yaml
from yaml import YAMLError

def validate_yaml(yaml_content):
    try:
        yaml.safe_load(yaml_content)
        return {"valid": True, "message": "Valid YAML"}
    except YAMLError as e:
        return {"valid": False, "message": str(e)}

def format_yaml(yaml_content):
    try:
        parsed = yaml.safe_load(yaml_content)
        return {
            "success": True,
            "formatted": yaml.dump(parsed, sort_keys=False, indent=2)
        }
    except YAMLError as e:
        return {"success": False, "error": str(e)}