# import jwt
# import base64
# import json
# from datetime import datetime
#
#
# def decode_jwt(token, verify_signature=False, secret=None):
#     """Decode JWT token with optional signature verification"""
#     try:
#         decoded = jwt.decode(
#             token,
#             secret,
#             algorithms=["HS256"],
#             options={"verify_signature": verify_signature}
#         )
#
#         # Get header without verification
#         header = jwt.get_unverified_header(token)
#
#         return {
#             "success": True,
#             "header": header,
#             "payload": decoded,
#             "is_expired": check_jwt_expiry(decoded)
#         }
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
#
# def check_jwt_expiry(payload):
#     """Check if JWT is expired"""
#     if 'exp' in payload:
#         return payload['exp'] < datetime.now().timestamp()
#     return False
#
#
# # Test Example:
# if __name__ == "__main__":
#     test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
#     print("JWT Decoded:", decode_jwt(test_token))

import jwt
import base64
import json
from datetime import datetime


# def decode_jwt(token, verify=False, secret=None):
#     """Decode JWT with optional signature verification"""
#     try:
#         # Get unverified header first
#         header = jwt.get_unverified_header(token)
#
#         # Decode payload
#         payload = jwt.decode(
#             token,
#             secret if verify else None,
#             options={"verify_signature": verify},
#             algorithms=[header.get('alg', 'HS256')]
#         )
#
#         # Pretty print components
#         header_str = json.dumps(header, indent=2)
#         payload_str = json.dumps(payload, indent=2)
#
#         # Check expiration if exists
#         is_expired = False
#         if 'exp' in payload:
#             is_expired = payload['exp'] < datetime.now().timestamp()
#
#         return {
#             'success': True,
#             'header': header_str,
#             'payload': payload_str,
#             'is_expired': is_expired,
#             'signature_valid': verify
#         }
#     except Exception as e:
#         return {'success': False, 'error': str(e)}

import jwt
import json
from datetime import datetime
import argparse


def decode_jwt(token, verify=False, secret=None):
    """Core decoding function"""
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(
            token,
            secret if verify else None,
            options={"verify_signature": verify},
            algorithms=[header.get('alg', 'HS256')]
        )
        return {
            'success': True,
            'header': json.dumps(header, indent=2),
            'payload': json.dumps(payload, indent=2),
            'is_expired': 'exp' in payload and payload['exp'] < datetime.now().timestamp()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def cli_test():
    """Command line testing interface"""
    parser = argparse.ArgumentParser(description='JWT Decoder')
    parser.add_argument('token', help='JWT token to decode')
    parser.add_argument('--verify', action='store_true', help='Verify signature')
    parser.add_argument('--secret', help='Verification secret')

    args = parser.parse_args()
    result = decode_jwt(args.token, args.verify, args.secret)

    if result['success']:
        print("=== Header ===")
        print(result['header'])
        print("\n=== Payload ===")
        print(result['payload'])
        if result['is_expired']:
            print("\n⚠️  Token is expired")
    else:
        print(f"Error: {result['error']}")


if __name__ == '__main__':
    cli_test()