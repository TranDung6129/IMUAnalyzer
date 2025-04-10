# tests/integration/test_serial_integration.py
import pytest
import serial
import time
import os
import sys
from unittest.mock import patch  # Thiếu import này trong file gốc

# Thêm src vào sys.path nếu cần thiết
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils import serial_utils
from src.utils.serial_utils import SerialConnectionError

# --- Cấu hình Test ---
WITMOTION_VID = 6790
WITMOTION_PID = 29987
TARGET_PORT = None  # Sẽ được tự động tìm

# Các tham số khác
DEFAULT_BAUDRATE = 115200
NON_EXISTENT_PORT = "COM_DOES_NOT_EXIST_XYZ"

# --- Pytest Fixture để tìm cổng trước khi chạy test ---
@pytest.fixture(scope="module", autouse=True)
def find_target_port():
    """Tự động tìm cổng serial của cảm biến trước khi chạy test."""
    global TARGET_PORT
    if TARGET_PORT:
        print(f"\n[INFO] Using pre-defined target port: {TARGET_PORT}")
        if not serial_utils.is_port_available(TARGET_PORT):
             pytest.skip(f"Pre-defined port {TARGET_PORT} is not available or already in use. Skipping integration tests.")
        return

    if WITMOTION_VID is None or WITMOTION_PID is None:
        pytest.skip("Target port not specified and WITMOTION_VID/PID not set. Skipping integration tests.")
        return

    print(f"\n[INFO] Attempting to find port with VID={WITMOTION_VID:#0x}, PID={WITMOTION_PID:#0x}...")
    all_ports = serial_utils.list_serial_ports()
    found_ports = serial_utils.find_imu_ports(all_ports, vid=WITMOTION_VID, pid=WITMOTION_PID)

    if not found_ports:
        pytest.skip(f"No serial port found with VID={WITMOTION_VID:#0x} PID={WITMOTION_PID:#0x}. Ensure sensor is connected. Skipping tests.")
    elif len(found_ports) > 1:
        print(f"[WARNING] Multiple ports found: {[p['device'] for p in found_ports]}. Using the first one: {found_ports[0]['device']}")
        TARGET_PORT = found_ports[0]['device']
    else:
        TARGET_PORT = found_ports[0]['device']
        print(f"[INFO] Found target port: {TARGET_PORT}")

    # Kiểm tra xem cổng có sẵn không trước khi chạy
    if not serial_utils.is_port_available(TARGET_PORT):
         pytest.skip(f"Target port {TARGET_PORT} was found but is not available (already in use?). Skipping integration tests.")


# --- Lớp Test ---
@pytest.mark.hardware
class TestSerialHardwareIntegration:

    def setup_method(self, method):
        """Chạy trước mỗi test method. Đảm bảo cổng không bị mở."""
        if not TARGET_PORT:
             pytest.skip("Target port not determined.")
        # Cố gắng đóng cổng nếu nó đang mở từ test trước đó bị lỗi
        try:
            conn = serial.Serial(TARGET_PORT)
            if conn.is_open:
                conn.close()
        except serial.SerialException:
            pass
        print(f"\n--- Running test: {method.__name__} ---")
        print(f"Target port for test: {TARGET_PORT}")


    def teardown_method(self, method):
        """Chạy sau mỗi test method. Đảm bảo cổng được đóng."""
        if not TARGET_PORT:
            return
        # Cố gắng đóng lại lần nữa để đảm bảo sạch sẽ
        try:
            conn_check = serial.Serial(TARGET_PORT, timeout=0.1)
            if conn_check.is_open:
                print(f"[TEARDOWN] Port {TARGET_PORT} was left open. Closing.")
                conn_check.close()
            else:
                 print(f"[TEARDOWN] Port {TARGET_PORT} confirmed closed.")
        except serial.SerialException:
             print(f"[TEARDOWN] Port {TARGET_PORT} likely already closed or unavailable.")
             pass


    # --- Test Cases ---
    def test_01_port_detection(self):
        """Kiểm tra list_serial_ports và find_imu_ports có thấy cổng mục tiêu."""
        assert TARGET_PORT is not None, "Setup fixture failed to find target port"

        all_ports = serial_utils.list_serial_ports()
        print(f"All detected ports: {[p['device'] for p in all_ports]}")
        assert any(p['device'] == TARGET_PORT for p in all_ports), f"Target port {TARGET_PORT} not found in list_serial_ports"

        if WITMOTION_VID and WITMOTION_PID:
             found_ports = serial_utils.find_imu_ports(all_ports, vid=WITMOTION_VID, pid=WITMOTION_PID)
             assert any(p['device'] == TARGET_PORT for p in found_ports), f"Target port {TARGET_PORT} not found by find_imu_ports with VID/PID"


    def test_02_open_close_cycle(self):
        """Kiểm tra mở và đóng kết nối thành công."""
        assert TARGET_PORT is not None
        print(f"Attempting to open {TARGET_PORT} at {DEFAULT_BAUDRATE} baud...")
        conn = None
        try:
            conn = serial_utils.open_serial_connection(TARGET_PORT, DEFAULT_BAUDRATE, retry_count=2, timeout=0.5)
            assert conn is not None, "open_serial_connection returned None"
            assert isinstance(conn, serial.Serial), "Returned object is not a serial.Serial instance"
            assert conn.is_open, "Serial connection is not open after open_serial_connection"
            assert conn.port == TARGET_PORT
            assert conn.baudrate == DEFAULT_BAUDRATE
            print(f"Successfully opened {TARGET_PORT}.")

            # Thêm test đọc dữ liệu để xác nhận giao tiếp
            conn.flushInput()
            time.sleep(0.2)
            data_in = conn.read(conn.in_waiting or 10)
            print(f"Read {len(data_in)} bytes: {data_in.hex() if data_in else 'None'}")
            # Không assert vì có thể không có dữ liệu ngay lập tức

        finally:
            if conn and conn.is_open:
                print(f"Attempting to close {TARGET_PORT}...")
                serial_utils.close_serial_connection(conn)
                assert not conn.is_open, "Serial connection is still open after close_serial_connection"
                print(f"Successfully closed {TARGET_PORT}.")
            elif conn:
                 print(f"Connection object exists but is not open, no need to close.")
            else:
                 print(f"Connection was not successfully established.")


    def test_03_get_status(self):
        """Kiểm tra get_connection_status trả về trạng thái đúng."""
        assert TARGET_PORT is not None
        conn = None
        # Trạng thái ban đầu (nên là disconnected nếu teardown hoạt động tốt)
        initial_status = serial_utils.get_connection_status(None) # Test với None trước
        assert not initial_status['connected']

        try:
            conn = serial_utils.open_serial_connection(TARGET_PORT, DEFAULT_BAUDRATE, timeout=0.5)
            status_open = serial_utils.get_connection_status(conn)
            print(f"Status (Open): {status_open}")
            assert status_open['connected'] is True
            assert status_open['port'] == TARGET_PORT
            assert status_open.get('error') is None

            # Thêm test cho các thuộc tính khác trong status
            assert 'baudrate' in status_open, "Status should contain baudrate"
            assert status_open['baudrate'] == DEFAULT_BAUDRATE
            assert 'timeout' in status_open, "Status should contain timeout"
            
        finally:
            if conn and conn.is_open:
                serial_utils.close_serial_connection(conn)
                time.sleep(0.1)
                assert not conn.is_open, "Connection should be closed"
                
                # Kiểm tra trạng thái đã đóng
                try:
                    conn_check = serial.Serial(TARGET_PORT, timeout=0.1)
                    status_recheck = serial_utils.get_connection_status(conn_check)
                    assert status_recheck['connected'] is True
                    conn_check.close()
                except serial.SerialException:
                    pass


    def test_04_open_non_existent_port(self):
        """Kiểm tra mở cổng không tồn tại sẽ raise lỗi sau retry."""
        print(f"Attempting to open non-existent port: {NON_EXISTENT_PORT}")
        # Patch time.sleep để test chạy nhanh
        with patch('src.utils.serial_utils.time.sleep'):
             with pytest.raises(SerialConnectionError) as excinfo:
                 serial_utils.open_serial_connection(NON_EXISTENT_PORT, DEFAULT_BAUDRATE, retry_count=2, timeout=0.1)
        print(f"Received expected exception: {excinfo.value}")
        assert f"Failed to open serial port {NON_EXISTENT_PORT}" in str(excinfo.value)
        
        # Thêm test với retry_count=0 để đảm bảo lỗi xảy ra ngay lập tức
        with pytest.raises(SerialConnectionError):
            serial_utils.open_serial_connection(NON_EXISTENT_PORT, DEFAULT_BAUDRATE, retry_count=0, timeout=0.1)


    def test_05_is_port_available(self):
        """Kiểm tra is_port_available hoạt động đúng."""
        assert TARGET_PORT is not None
        # Ban đầu, cổng nên có sẵn (nếu setup/teardown hoạt động)
        assert serial_utils.is_port_available(TARGET_PORT), f"Port {TARGET_PORT} should be available initially"

        conn = None
        try:
            # Mở cổng
            conn = serial.Serial(TARGET_PORT, DEFAULT_BAUDRATE)
            assert conn.is_open
            # Kiểm tra lại khi cổng đang mở - hành vi phụ thuộc OS
            is_avail_while_open = serial_utils.is_port_available(TARGET_PORT)
            print(f"is_port_available result while open: {is_avail_while_open}")
            # Không assert is_avail_while_open vì có thể OS trả về True hoặc False

        finally:
            if conn and conn.is_open:
                conn.close()
            time.sleep(0.1)

        # Kiểm tra lại sau khi đóng
        assert serial_utils.is_port_available(TARGET_PORT), f"Port {TARGET_PORT} should be available after closing"

        # Kiểm tra cổng không tồn tại
        assert not serial_utils.is_port_available(NON_EXISTENT_PORT), f"Non-existent port {NON_EXISTENT_PORT} should not be available"
    
    
    # Thêm test mới để check timeout
    def test_06_connection_timeout(self):
        """Kiểm tra timeout khi đọc dữ liệu."""
        assert TARGET_PORT is not None
        conn = None
        try:
            # Mở kết nối với timeout ngắn
            conn = serial_utils.open_serial_connection(TARGET_PORT, DEFAULT_BAUDRATE, timeout=0.1)
            assert conn.timeout == 0.1, "Timeout not set correctly"
            
            # Đọc với timeout - nên trả về bytes rỗng nếu không có dữ liệu
            start_time = time.time()
            data = conn.read(10)  # Đọc 10 bytes hoặc timeout
            end_time = time.time()
            
            # Kiểm tra thời gian đọc có xấp xỉ timeout không
            elapsed = end_time - start_time
            print(f"Read operation took {elapsed:.3f}s with timeout 0.1s")
            assert elapsed < 0.2, "Read took too long, timeout may not be working"
            
            # Có thể có hoặc không có dữ liệu, không assert cụ thể
            print(f"Read returned {len(data)} bytes: {data.hex() if data else 'None'}")
            
        finally:
            if conn and conn.is_open:
                serial_utils.close_serial_connection(conn)


    # Test reconnect và wait_for_port bị bỏ qua vì yêu cầu tương tác thủ công
    @pytest.mark.skip(reason="Reconnect test requires manual intervention")
    def test_07_reconnect_manual(self):
        """Kiểm tra reconnect (YÊU CẦU TƯƠNG TÁC THỦ CÔNG)."""
        pass  # Giữ lại để người dùng có thể mở skip riêng cho test này


    @pytest.mark.skip(reason="wait_for_port test requires manual intervention")
    def test_08_wait_for_port_manual(self):
        """Kiểm tra wait_for_port (YÊU CẦU TƯƠNG TÁC THỦ CÔNG)."""
        pass  # Giữ lại để người dùng có thể mở skip riêng cho test này