import re


def curl_to_python(curl_command):
    """Convert cURL command to Python requests code"""
    try:
        # Extract URL
        url_match = re.search(r"curl ['\"]([^'\"]+)['\"]", curl_command)
        if not url_match:
            url_match = re.search(r"curl (https?://\S+)", curl_command)
        if not url_match:
            return {"success": False, "error": "URL not found in cURL command"}

        url = url_match.group(1)

        # Extract headers
        headers = {}
        header_matches = re.finditer(r"-H ['\"]([^'\"]+)['\"]", curl_command)
        for match in header_matches:
            header = match.group(1).split(': ')
            headers[header[0]] = header[1]

        # Extract data
        data = None
        data_match = re.search(r"--data ['\"]([^'\"]+)['\"]", curl_command)
        if data_match:
            data = data_match.group(1)

        # Build Python code
        code = "import requests\n\n"
        code += f"url = '{url}'\n"

        if headers:
            code += "headers = {\n"
            for k, v in headers.items():
                code += f"    '{k}': '{v}',\n"
            code += "}\n\n"
        else:
            code += "headers = None\n\n"

        if data:
            code += f"data = '{data}'\n\n"

        code += "response = requests.request(\n"
        code += "    method='POST' if data else 'GET',\n"
        code += "    url=url,\n"
        code += "    headers=headers,\n"
        code += "    data=data\n"
        code += ")\n\n"
        code += "print(response.text)"

        return {"success": True, "code": code}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Test Example:
if __name__ == "__main__":
    curl_example = """curl -X POST 'https://api.example.com/login' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer token123' \
--data '{"username":"admin","password":"secret"}'"""

    print(curl_to_python(curl_example)["code"])