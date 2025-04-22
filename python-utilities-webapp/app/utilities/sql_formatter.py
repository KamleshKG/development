# import sqlparse
#
# def format_sql(sql, indent_width=2):
#     """Format SQL query with proper indentation"""
#     try:
#         formatted = sqlparse.format(
#             sql,
#             reindent=True,
#             indent_width=indent_width,
#             keyword_case='upper'
#         )
#         return {"success": True, "formatted": formatted}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
# # Test Example:
# if __name__ == "__main__":
#     ugly_sql = "SELECT * FROM users WHERE id=1 ORDER BY name;"
#     print("Formatted SQL:", format_sql(ugly_sql)["formatted"])

# import sqlparse
#
# def format_sql(sql, indent_width=2, keyword_case='upper'):
#     """Format SQL with customizable indentation and keyword casing"""
#     try:
#         formatted = sqlparse.format(
#             sql,
#             reindent=True,
#             indent_width=indent_width,
#             keyword_case=keyword_case,
#             use_space_around_operators=True,
#             strip_comments=False
#         )
#         return {
#             'success': True,
#             'formatted': formatted,
#             'stats': {
#                 'lines': len(formatted.split('\n')),
#                 'length': len(formatted),
#                 'keywords': sum(1 for word in sqlparse.parse(formatted)[0].flatten()
#                               if word.ttype is sqlparse.tokens.Keyword)
#             }
#         }
#     except Exception as e:
#         return {'success': False, 'error': str(e)}

import sqlparse
import argparse


def format_sql(sql, indent_width=2, keyword_case='upper'):
    """Core formatting function"""
    try:
        formatted = sqlparse.format(
            sql,
            reindent=True,
            indent_width=indent_width,
            keyword_case=keyword_case
        )
        return {
            'success': True,
            'formatted': formatted,
            'stats': {
                'lines': len(formatted.split('\n')),
                'length': len(formatted)
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def cli_test():
    """Command line testing interface"""
    parser = argparse.ArgumentParser(description='SQL Formatter')
    parser.add_argument('sql', help='SQL query to format')
    parser.add_argument('--indent', type=int, default=2, help='Indentation width')
    parser.add_argument('--case', choices=['upper', 'lower'], default='upper', help='Keyword case')

    args = parser.parse_args()
    result = format_sql(args.sql, args.indent, args.case)

    if result['success']:
        print("=== Formatted SQL ===")
        print(result['formatted'])
        print(f"\nStats: {result['stats']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == '__main__':
    cli_test()