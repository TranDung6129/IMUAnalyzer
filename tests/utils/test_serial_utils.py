import unittest
from unittest.mock import patch, MagicMock, call
import serial 
import time

from src.utils import serial_utils
from src.utils.serial_utils import SerialConnectionError 

class TestSerialUtils(unittest.TestCase):

    @patch('src.utils.serial_utils.serial.Serial') 
    def test_open_serial_connection_success(self, mock_serial_class):
        """
        Kiểm tra mở kết nối thành công ngay lần đầu.
        """
        mock_instance = MagicMock()
        mock_instance.is_open = True
        mock_serial_class.return_value = mock_instance 

        port = "/dev/ttyUSB0test"
        baudrate = 115200
        ser = serial_utils.open_serial_connection(port, baudrate, retry_count=1)

        # Kiểm tra xem serial.Serial có được gọi với đúng tham số không
        mock_serial_class.assert_called_once_with(port=port, baudrate=baudrate, timeout=1.0)
        
        # Kiểm tra xem instance trả về có phải là mock_instance không
        self.assertEqual(ser, mock_instance)
        
        # Kiểm tra is_open không được gọi lại (vì mock đã trả về True)
        mock_instance.open.assert_not_called()
        # Kiểm tra time.sleep có được gọi không (chỉ gọi sau khi thành công)
        # Dùng patch time.sleep nếu muốn kiểm tra chính xác thời gian sleep
        # @patch('src.utils.serial_utils.time.sleep')

    @patch('src.utils.serial_utils.serial.Serial')
    @patch('src.utils.serial_utils.time.sleep')
    def test_open_serial_connection_retry_success(self, mock_sleep, mock_serial_class):
        """Kiểm tra mở kết nối thành công sau khi retry."""
        mock_instance_success = MagicMock()
        mock_instance_success.is_open = True
        
        mock_serial_class.side_effect = [serial.SerialException("Fail 1"), mock_instance_success]
        
        port = 'COM_RETRY'
        baudrate = 115200
        ser = serial_utils.open_serial_connection(port, baudrate, retry_count=3)
        
        self.assertEqual(mock_serial_class.call_count, 2)
        mock_serial_class.assert_has_calls([
            call(port=port, baudrate=baudrate, timeout=1.0),
            call(port=port, baudrate=baudrate, timeout=1.0)
        ])
        
        # Update to expect two calls with the correct arguments
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_has_calls([
            call(0.5),  # First call after failure
            call(0.1)   # Second call after success
        ])
        
        self.assertEqual(ser, mock_instance_success)

    @patch('src.utils.serial_utils.serial.Serial')
    def test_close_serial_connection(self, mock_serial_class):
        """Kiểm tra đóng kết nối thành công."""
        mock_instance = MagicMock()
        mock_instance.is_open = True
        # Không cần mock_serial_class.return_value vì ta truyền instance vào

        serial_utils.close_serial_connection(mock_instance)

        # Kiểm tra các phương thức của instance mock được gọi
        mock_instance.flush.assert_called_once()
        mock_instance.close.assert_called_once()

    @patch('src.utils.serial_utils.serial.Serial')
    def test_close_serial_connection_already_closed(self, mock_serial_class):
        """Kiểm tra đóng kết nối khi nó đã đóng sẵn."""
        mock_instance = MagicMock()
        mock_instance.is_open = False # Giả lập cổng đã đóng

        serial_utils.close_serial_connection(mock_instance)

        # flush và close không nên được gọi nếu is_open là False
        mock_instance.flush.assert_not_called()
        mock_instance.close.assert_not_called()

    @patch('src.utils.serial_utils.serial.Serial')
    def test_close_serial_connection_raises_error(self, mock_serial_class):
        """Kiểm tra xử lý lỗi khi đóng."""
        mock_instance = MagicMock()
        mock_instance.is_open = True
        mock_instance.close.side_effect = serial.SerialException("Error during close")

        with self.assertRaises(SerialConnectionError) as cm:
            serial_utils.close_serial_connection(mock_instance)

        mock_instance.flush.assert_called_once() # flush vẫn được gọi trước khi close lỗi
        self.assertIn("Failed to close serial connection", str(cm.exception))

    @patch('src.utils.serial_utils.serial.tools.list_ports.comports')
    def test_list_serial_ports(self, mock_comports):
        """Kiểm tra hàm list_serial_ports."""
        # Tạo dữ liệu giả lập trả về từ comports()
        mock_port1 = MagicMock()
        mock_port1.device = '/dev/ttyS0'
        mock_port1.name = 'ttyS0'
        mock_port1.description = 'Serial Port 0'
        mock_port1.hwid = 'PNP0501'
        mock_port1.vid = None
        mock_port1.pid = None

        mock_port2 = MagicMock()
        mock_port2.device = '/dev/ttyUSB0'
        mock_port2.name = 'ttyUSB0'
        mock_port2.description = 'USB Serial Device'
        mock_port2.hwid = 'USB VID:PID=1A86:7523'
        mock_port2.vid = 0x1A86
        mock_port2.pid = 0x7523

        mock_comports.return_value = [mock_port1, mock_port2]

        ports = serial_utils.list_serial_ports()

        self.assertEqual(len(ports), 2)
        self.assertEqual(ports[0]['device'], '/dev/ttyS0')
        self.assertEqual(ports[1]['device'], '/dev/ttyUSB0')
        self.assertEqual(ports[1]['vid'], 0x1A86)

    @patch('src.utils.serial_utils.serial.Serial')
    def test_is_port_available_true(self, mock_serial_class):
        mock_instance = MagicMock()
        mock_serial_class.return_value = mock_instance

        self.assertTrue(serial_utils.is_port_available('COM_OK'))
        mock_serial_class.assert_called_once_with('COM_OK', timeout=0.1)
        mock_instance.close.assert_called_once() # Đảm bảo close được gọi

    @patch('src.utils.serial_utils.serial.Serial')
    def test_is_port_available_false(self, mock_serial_class):
        mock_serial_class.side_effect = serial.SerialException("Cannot open port")

        self.assertFalse(serial_utils.is_port_available('COM_BAD'))
        mock_serial_class.assert_called_once_with('COM_BAD', timeout=0.1)

    @patch('src.utils.serial_utils.open_serial_connection') # Mock hàm open nội bộ
    def test_reconnect_success(self, mock_open):
        """Kiểm tra reconnect thành công."""
        mock_old_conn = MagicMock(spec=serial.Serial) # Spec để mock có các thuộc tính/method của serial.Serial
        mock_old_conn.port = 'COM_RECONNECT'
        mock_old_conn.baudrate = 115200
        mock_old_conn.timeout = 1.5
        mock_old_conn.is_open = True

        mock_new_conn = MagicMock(spec=serial.Serial)
        mock_open.return_value = mock_new_conn # open_serial_connection trả về kết nối mới

        new_ser = serial_utils.reconnect(mock_old_conn, max_attempts=2)

        # Kiểm tra close được gọi trên kết nối cũ
        mock_old_conn.close.assert_called_once()
        # Kiểm tra open_serial_connection được gọi với đúng tham số gốc
        mock_open.assert_called_once_with('COM_RECONNECT', 115200, 1.5, 2)
        # Kiểm tra kết quả là kết nối mới
        self.assertEqual(new_ser, mock_new_conn)

    @patch('src.utils.serial_utils.open_serial_connection')
    def test_reconnect_close_fails_but_open_succeeds(self, mock_open):
        """Kiểm tra reconnect vẫn thử open ngay cả khi close lỗi."""
        mock_old_conn = MagicMock(spec=serial.Serial)
        mock_old_conn.port = 'COM_X'
        mock_old_conn.baudrate = 9600
        mock_old_conn.timeout = 1.0
        mock_old_conn.is_open = True
        mock_old_conn.close.side_effect = serial.SerialException("Close error") # Giả lập lỗi khi close

        mock_new_conn = MagicMock(spec=serial.Serial)
        mock_open.return_value = mock_new_conn

        new_ser = serial_utils.reconnect(mock_old_conn)

        mock_old_conn.close.assert_called_once() # Vẫn gọi close
        # Quan trọng: open vẫn được gọi dù close lỗi
        mock_open.assert_called_once_with('COM_X', 9600, 1.0, 3) # Dùng default retries
        self.assertEqual(new_ser, mock_new_conn)

    @patch('src.utils.serial_utils.open_serial_connection')
    def test_reconnect_open_fails(self, mock_open):
        """Kiểm tra reconnect thất bại nếu open_serial_connection thất bại."""
        mock_old_conn = MagicMock(spec=serial.Serial)
        mock_old_conn.port = 'COM_FAIL_OPEN'
        # ... set các thuộc tính khác ...
        mock_old_conn.is_open = True

        # Giả lập open_serial_connection raise lỗi
        mock_open.side_effect = SerialConnectionError("Failed to open from mock")

        with self.assertRaises(SerialConnectionError) as cm:
            serial_utils.reconnect(mock_old_conn)

        mock_old_conn.close.assert_called_once() # Close vẫn được gọi
        mock_open.assert_called_once() # Open được gọi
        self.assertIn("Failed to open from mock", str(cm.exception))

    def test_reconnect_input_none(self):
        """Kiểm tra raise lỗi nếu input là None."""
        with self.assertRaises(SerialConnectionError) as cm:
            serial_utils.reconnect(None)
        self.assertIn("No serial connection to reconnect", str(cm.exception))

class TestSerialUtilsGetStatus(unittest.TestCase):

    def test_get_connection_status_connected(self):
        """Kiểm tra trạng thái khi kết nối thành công."""
        mock_conn = MagicMock(spec=serial.Serial)
        mock_conn.is_open = True
        mock_conn.port = 'COM_STATUS'
        mock_conn.baudrate = 115200
        mock_conn.timeout = 0.5
        # Giả lập giá trị trả về cho thuộc tính waiting (có thể thay đổi)
        type(mock_conn).in_waiting = unittest.mock.PropertyMock(return_value=10)
        type(mock_conn).out_waiting = unittest.mock.PropertyMock(return_value=5)

        status = serial_utils.get_connection_status(mock_conn)

        self.assertEqual(status, {
            "connected": True,
            "port": 'COM_STATUS',
            "baudrate": 115200,
            "timeout": 0.5,
            "in_waiting": 10,
            "out_waiting": 5
        })

    def test_get_connection_status_disconnected(self):
        """Kiểm tra trạng thái khi không kết nối."""
        mock_conn = MagicMock(spec=serial.Serial)
        mock_conn.is_open = False
        mock_conn.port = 'COM_DISC'
        mock_conn.baudrate = 9600
        mock_conn.timeout = 1.0
        # Giả lập giá trị waiting khi không kết nối
        type(mock_conn).in_waiting = unittest.mock.PropertyMock(return_value=0)
        type(mock_conn).out_waiting = unittest.mock.PropertyMock(return_value=0)

        status = serial_utils.get_connection_status(mock_conn)

        self.assertEqual(status, {
            "connected": False,
            "port": 'COM_DISC',
            "baudrate": 9600,
            "timeout": 1.0,
            "in_waiting": 0,
            "out_waiting": 0
        })

    def test_get_connection_status_input_none(self):
        """Kiểm tra trạng thái khi input là None."""
        status = serial_utils.get_connection_status(None)
        self.assertEqual(status, {"connected": False, "error": "Connection is None"})

    def test_get_connection_status_exception_on_access(self):
        """Kiểm tra trạng thái khi truy cập thuộc tính của serial lỗi."""
        mock_conn = MagicMock(spec=serial.Serial)
        mock_conn.is_open = True # Giả sử đang mở nhưng có lỗi khác
        mock_conn.port = 'COM_ERR'
        # Giả lập lỗi khi truy cập in_waiting
        type(mock_conn).in_waiting = unittest.mock.PropertyMock(side_effect=serial.SerialException("Access Error"))

        status = serial_utils.get_connection_status(mock_conn)

        self.assertEqual(status, {
            "connected": False, # Chuyển thành False khi có lỗi
            "error": "Access Error"
        })

class TestSerialUtilsWaitForPort(unittest.TestCase):

    @patch('src.utils.serial_utils.time.sleep')
    @patch('src.utils.serial_utils.is_port_available')
    @patch('src.utils.serial_utils.time.time') # Mock time.time để kiểm soát timeout
    def test_wait_for_port_available_immediately(self, mock_time, mock_is_available, mock_sleep):
        """Kiểm tra khi cổng có sẵn ngay lập tức."""
        mock_is_available.return_value = True
        mock_time.return_value = 100.0 # Thời gian bắt đầu giả lập

        result = serial_utils.wait_for_port('COM_WAIT', timeout=5.0)

        self.assertTrue(result)
        mock_is_available.assert_called_once_with('COM_WAIT')
        mock_sleep.assert_not_called() # Không cần sleep

    @patch('src.utils.serial_utils.time.sleep')
    @patch('src.utils.serial_utils.is_port_available')
    @patch('src.utils.serial_utils.time.time')
    def test_wait_for_port_available_after_delay(self, mock_time, mock_is_available, mock_sleep):
        """Kiểm tra khi cổng có sẵn sau vài lần thử."""
        # Giả lập is_port_available trả về False 2 lần, rồi True
        mock_is_available.side_effect = [False, False, True]
        # Giả lập thời gian tăng dần để không bị timeout ngay
        mock_time.side_effect = [100.0, 100.1, 100.7, 101.3] # Thời gian bắt đầu và sau mỗi sleep

        result = serial_utils.wait_for_port('COM_WAIT_DELAY', timeout=5.0, interval=0.5)

        self.assertTrue(result)
        # Kiểm tra is_port_available được gọi 3 lần
        self.assertEqual(mock_is_available.call_count, 3)
        mock_is_available.assert_has_calls([call('COM_WAIT_DELAY'), call('COM_WAIT_DELAY'), call('COM_WAIT_DELAY')])
        # Kiểm tra sleep được gọi 2 lần với đúng interval
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_has_calls([call(0.5), call(0.5)])

    @patch('src.utils.serial_utils.time.sleep')
    @patch('src.utils.serial_utils.is_port_available')
    @patch('src.utils.serial_utils.time.time')
    def test_wait_for_port_timeout(self, mock_time, mock_is_available, mock_sleep):
        """Kiểm tra khi hết thời gian chờ mà cổng vẫn chưa có."""
        mock_is_available.return_value = False # Luôn trả về False
        # Giả lập thời gian trôi qua timeout
        start_time = 100.0
        timeout_duration = 2.0
        # Các giá trị time.time() giả lập, lần cuối cùng vượt quá timeout
        mock_time.side_effect = [start_time, start_time + 0.1, start_time + 0.6, start_time + 1.1, start_time + 1.6, start_time + 2.1]

        result = serial_utils.wait_for_port('COM_TIMEOUT', timeout=timeout_duration, interval=0.5)

        self.assertFalse(result)
        # Kiểm tra is_port_available được gọi nhiều lần
        self.assertGreater(mock_is_available.call_count, 3) # Số lần gọi phụ thuộc vào interval
        # Kiểm tra sleep được gọi nhiều lần
        self.assertGreater(mock_sleep.call_count, 3)

if __name__ == '__main__':
    unittest.main()