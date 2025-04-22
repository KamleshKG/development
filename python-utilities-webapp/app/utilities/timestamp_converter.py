# from datetime import datetime
#
#
# def timestamp_to_datetime(ts, unit='s'):
#     """Convert timestamp to human-readable datetime"""
#     try:
#         if unit == 'ms':
#             ts = float(ts) / 1000
#         elif unit == 'µs':
#             ts = float(ts) / 1_000_000
#         elif unit == 'ns':
#             ts = float(ts) / 1_000_000_000
#
#         return {
#             "success": True,
#             "datetime": datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S'),
#             "isoformat": datetime.fromtimestamp(float(ts)).isoformat()
#         }
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
#
# def datetime_to_timestamp(dt_str, unit='s'):
#     """Convert datetime string to timestamp"""
#     try:
#         dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         ts = dt.timestamp()
#
#         if unit == 'ms':
#             ts = ts * 1000
#         elif unit == 'µs':
#             ts = ts * 1_000_000
#         elif unit == 'ns':
#             ts = ts * 1_000_000_000
#
#         return {"success": True, "timestamp": ts}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
#
# # Test Example:
# if __name__ == "__main__":
#     print("Current timestamp:", datetime_to_timestamp("2023-01-01 12:00:00"))
#     print("From timestamp:", timestamp_to_datetime("1672574400"))

from datetime import datetime
import pytz
import argparse


def convert_timestamp(ts, input_unit='s', output_tz='UTC'):
    """Core conversion function"""
    try:
        ts = float(ts)
        if input_unit == 'ms':
            ts /= 1000
        elif input_unit == 'µs':
            ts /= 1_000_000
        elif input_unit == 'ns':
            ts /= 1_000_000_000

        dt_utc = datetime.utcfromtimestamp(ts)
        dt_local = dt_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(output_tz))

        return {
            'success': True,
            'results': {
                'datetime_utc': dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'datetime_local': dt_local.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'timestamp_s': int(ts),
                'timestamp_ms': int(ts * 1000)
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def cli_test():
    """Command line testing interface"""
    parser = argparse.ArgumentParser(description='Timestamp Converter')
    parser.add_argument('timestamp', help='Timestamp to convert')
    parser.add_argument('--unit', choices=['s', 'ms', 'µs', 'ns'], default='s', help='Input unit')
    parser.add_argument('--tz', default='UTC', help='Output timezone')

    args = parser.parse_args()
    result = convert_timestamp(args.timestamp, args.unit, args.tz)

    if result['success']:
        print("=== Conversion Results ===")
        print(f"UTC Time: {result['results']['datetime_utc']}")
        print(f"Local Time ({args.tz}): {result['results']['datetime_local']}")
        print(f"\nEquivalent Timestamps:")
        print(f"Seconds: {result['results']['timestamp_s']}")
        print(f"Milliseconds: {result['results']['timestamp_ms']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == '__main__':
    cli_test()