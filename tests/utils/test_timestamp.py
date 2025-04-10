# tests/utils/test_simple_timestamp.py
import unittest
from datetime import datetime, timezone, timedelta
import time
from src.utils import timestamp_utils

class TestSimpleTimestamp(unittest.TestCase):
    def test_generate_timestamp_all_modes(self):
        """Test tất cả các chế độ của generate_timestamp."""
        # Test realtime
        realtime = timestamp_utils.generate_timestamp(mode='realtime')
        self.assertIsInstance(realtime, str)
        self.assertEqual(len(realtime.split(':')[-1]), 6)  # Kiểm tra format HH:MM:SS.mmm
        
        # Test với UTC offset
        realtime_utc = timestamp_utils.generate_timestamp(mode='realtime', utc_offset=0)
        self.assertIsInstance(realtime_utc, str)
        
        # Test packet
        packet = timestamp_utils.generate_timestamp(mode='packet', packet_count=100)
        self.assertEqual(packet, "100")
        
        # Test chiptime
        dt = datetime(2023, 5, 1, 14, 30, 45, 123456)
        chiptime = timestamp_utils.generate_timestamp(mode='chiptime', device_time=dt)
        self.assertEqual(chiptime, "14:30:45.123")
        
        # Test unix
        unix_ts = timestamp_utils.generate_timestamp(mode='unix')
        self.assertIsInstance(unix_ts, float)
        self.assertTrue(unix_ts > 0)
        
        # Test unix với start_time và packet_count
        expected = 1000.0 + (10 * 0.1)
        unix_rel = timestamp_utils.generate_timestamp(
            mode='unix',
            start_time=1000.0,
            packet_count=10,
            time_step=0.1
        )
        self.assertEqual(unix_rel, expected)
        
        # Test với invalid mode
        invalid = timestamp_utils.generate_timestamp(mode='invalid')
        self.assertIsInstance(invalid, float)
    
    def test_parse_timestamp(self):
        """Test chức năng parse_timestamp với các định dạng khác nhau."""
        # Test các định dạng chuẩn
        formats = [
            "2023-05-01 14:30:45.123",
            "2023-05-01 14:30:45",
            "14:30:45.123",
            "14:30:45",
            "20230501143045"
        ]
        
        for fmt in formats:
            dt = timestamp_utils.parse_timestamp(fmt)
            self.assertIsInstance(dt, datetime)
        
        # Test với format string
        dt_fmt = timestamp_utils.parse_timestamp("01/05/2023", format_str="%d/%m/%Y")
        self.assertEqual(dt_fmt.year, 2023)
        self.assertEqual(dt_fmt.month, 5)
        self.assertEqual(dt_fmt.day, 1)
        
        # Test với UTC offset
        dt_utc = timestamp_utils.parse_timestamp("2023-05-01 14:30:45", utc_offset=0)
        self.assertEqual(dt_utc.tzinfo, timezone.utc)
        
        # Test với UTC+7
        dt_utc7 = timestamp_utils.parse_timestamp("2023-05-01 14:30:45", utc_offset=7)
        self.assertEqual(dt_utc7.tzinfo, timezone(timedelta(hours=7)))
        
        # Test với Unix timestamp string
        now = time.time()
        dt_unix = timestamp_utils.parse_timestamp(str(now))
        self.assertIsInstance(dt_unix, datetime)
        
        # Test báo lỗi với định dạng không hợp lệ
        with self.assertRaises(ValueError):
            timestamp_utils.parse_timestamp("invalid format")
    
    def test_convert_timestamp(self):
        """Test convert_timestamp với các output format khác nhau."""
        test_dt = datetime(2023, 5, 1, 14, 30, 45, 123456)
        
        # Test convert to datetime
        dt_out = timestamp_utils.convert_timestamp(test_dt, output_format='datetime')
        self.assertEqual(dt_out, test_dt)
        
        # Test convert string to datetime
        dt_from_str = timestamp_utils.convert_timestamp("2023-05-01 14:30:45", output_format='datetime')
        self.assertIsInstance(dt_from_str, datetime)
        
        # Test convert float to datetime
        dt_from_float = timestamp_utils.convert_timestamp(time.time(), output_format='datetime')
        self.assertIsInstance(dt_from_float, datetime)
        
        # Test convert to string
        str_out = timestamp_utils.convert_timestamp(test_dt, output_format='string')
        self.assertEqual(str_out, "2023-05-01 14:30:45.123")
        
        # Test convert to unix
        unix_out = timestamp_utils.convert_timestamp(test_dt, output_format='unix')
        self.assertIsInstance(unix_out, float)
        
        # Test convert to isoformat
        iso_out = timestamp_utils.convert_timestamp(test_dt, output_format='isoformat')
        self.assertEqual(iso_out, test_dt.isoformat())
        
        # Test convert to RFC3339
        rfc_out = timestamp_utils.convert_timestamp(test_dt, output_format='rfc3339')
        self.assertTrue(rfc_out.endswith('Z'))  # Kiểm tra UTC
        
        # Test với UTC offset
        dt_with_utc = timestamp_utils.convert_timestamp(test_dt, output_format='datetime', utc_offset=0)
        self.assertEqual(dt_with_utc.tzinfo, timezone.utc)
        
        # Test báo lỗi với format không hợp lệ
        with self.assertRaises(ValueError):
            timestamp_utils.convert_timestamp(test_dt, output_format='invalid')

    def test_get_timestamp_from_packet(self):
        """Test lấy timestamp từ packet data."""
        # Test Unix 4 bytes
        ts = int(time.time())
        packet_data = ts.to_bytes(4, byteorder='little')
        dt_unix = timestamp_utils.get_timestamp_from_packet(packet_data, 0, 4, 'unix')
        self.assertIsInstance(dt_unix, datetime)
        
        # Test Unix 8 bytes (milliseconds)
        ts_ms = int(time.time() * 1000)
        packet_data_ms = ts_ms.to_bytes(8, byteorder='little')
        dt_unix_ms = timestamp_utils.get_timestamp_from_packet(packet_data_ms, 0, 8, 'unix')
        self.assertIsInstance(dt_unix_ms, datetime)
        
        # Test với UTC offset
        dt_unix_utc = timestamp_utils.get_timestamp_from_packet(packet_data, 0, 4, 'unix', utc_offset=0)
        self.assertEqual(dt_unix_utc.tzinfo, timezone.utc)
        
        # Test milliseconds format
        millis = 123456789  # 123.456789 seconds
        packet_data_millis = millis.to_bytes(4, byteorder='little')
        dt_millis = timestamp_utils.get_timestamp_from_packet(packet_data_millis, 0, 4, 'milliseconds')
        self.assertIsInstance(dt_millis, datetime)
        
        # Test format không xác định
        dt_unknown = timestamp_utils.get_timestamp_from_packet(b'\x01\x02\x03\x04', 0, 4, 'unknown')
        self.assertIsInstance(dt_unknown, datetime)
        
        # Test với UTC offset và format không xác định
        dt_unknown_utc = timestamp_utils.get_timestamp_from_packet(b'\x01\x02\x03\x04', 0, 4, 'unknown', utc_offset=0)
        self.assertEqual(dt_unknown_utc.tzinfo, timezone.utc)

if __name__ == '__main__':
    unittest.main()