# tests/utils/test_simple.py
import unittest
from datetime import datetime, timezone, timedelta
from src.utils import timestamp_utils

class TestTimestampWithUTC(unittest.TestCase):
    def test_generate_with_utc(self):
        # Test realtime với UTC offset
        timestamp = timestamp_utils.generate_timestamp(mode='realtime', utc_offset=0)
        self.assertIsInstance(timestamp, str)
        
        # Test unix với UTC offset
        unix_ts = timestamp_utils.generate_timestamp(mode='unix', utc_offset=7)
        self.assertIsInstance(unix_ts, float)
        
    def test_parse_with_utc(self):
        # Test parse với UTC
        dt = timestamp_utils.parse_timestamp("2023-05-01 12:30:45", utc_offset=0)
        self.assertEqual(dt.tzinfo, timezone.utc)
        
        # Test parse với UTC+7
        dt_utc7 = timestamp_utils.parse_timestamp("2023-05-01 12:30:45", utc_offset=7)
        self.assertEqual(dt_utc7.tzinfo, timezone(timedelta(hours=7)))
        
    def test_convert_with_utc(self):
        # Test convert với UTC
        dt = datetime(2023, 5, 1, 12, 30, 45)
        dt_with_tz = timestamp_utils.convert_timestamp(dt, output_format='datetime', utc_offset=0)
        self.assertEqual(dt_with_tz.tzinfo, timezone.utc)
        
        # Test convert to RFC3339 với UTC
        rfc = timestamp_utils.convert_timestamp(dt, output_format='rfc3339', utc_offset=0)
        self.assertTrue(rfc.endswith('Z'))  # Kiểm tra kết thúc bằng Z (UTC)

if __name__ == '__main__':
    unittest.main()