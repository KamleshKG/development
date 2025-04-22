#!/usr/bin/env python3
from app import create_app
from app.utilities import (
    sql_formatter,
    jwt_decoder,
    timestamp_converter
)
import argparse
import sys


def run_cli_tests():
    """Test utilities via command line"""
    print("\n" + "=" * 40)
    print("TESTING SQL FORMATTER".center(40))
    print("=" * 40)
    sql = "SELECT * FROM users WHERE id=1 ORDER BY name;"
    sql_result = sql_formatter.format_sql(sql, indent_width=4)
    print(f"Input SQL:\n{sql}")
    print(f"\nFormatted SQL:\n{sql_result['formatted']}")

    print("\n" + "=" * 40)
    print("TESTING JWT DECODER".center(40))
    print("=" * 40)
    test_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    jwt_result = jwt_decoder.decode_jwt(test_jwt)
    print(f"JWT Header:\n{jwt_result['header']}")
    print(f"\nJWT Payload:\n{jwt_result['payload']}")

    print("\n" + "=" * 40)
    print("TESTING TIMESTAMP CONVERTER".center(40))
    print("=" * 40)
    ts_result = timestamp_converter.convert_timestamp("1633036800", tz="America/New_York")
    print(f"UTC Time: {ts_result['results']['datetime_utc']}")
    print(f"New York Time: {ts_result['results']['datetime_local']}")


def start_web_app():
    """Start the Flask web application"""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python Utilities App')
    parser.add_argument('--cli', action='store_true', help='Run CLI tests instead of starting web server')

    args = parser.parse_args()

    if args.cli:
        run_cli_tests()
    else:
        print("Starting web server at http://localhost:5000")
        print("Available utilities:")
        print("- /sql-formatter")
        print("- /jwt-decoder")
        print("- /timestamp-converter")
        start_web_app()