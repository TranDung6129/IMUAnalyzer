# src/plugins/decoders/base_decoder.py
from abc import ABC, abstractmethod
from typing import Any, Generator, Dict
# Quan trọng: Import lớp SensorData chuẩn
from src.data.models import SensorData

class BaseDecoder(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các bộ giải mã dữ liệu (Decoders).

    Decoders nhận dữ liệu THÔ (bytes) từ Reader và chuyển đổi nó thành
    dữ liệu có cấu trúc (đối tượng SensorData chuẩn).
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo Decoder với cấu hình cụ thể.

        Args:
            config (Dict[str, Any]): Dictionary chứa các tham số cấu hình
                                     cho Decoder này (ví dụ: 'acc_range', 'gyro_range',
                                     'timestamp_mode', 'sensor_id').
        """
        self.config = config
        self.sensor_id = config.get('sensor_id', 'default_sensor') # Lấy sensor_id từ config
        print(f"Initializing {self.__class__.__name__} for sensor '{self.sensor_id}' with config: {config}")

    @abstractmethod
    def decode(self, raw_data: bytes) -> Generator[SensorData, None, None]:
        """
        Phương thức cốt lõi để giải mã dữ liệu thô.

        Phương thức này PHẢI được triển khai bởi các lớp con.
        Nó nhận một khối dữ liệu thô `raw_data` (bytes) từ Reader.
        Decoder có thể cần quản lý một buffer nội bộ để xử lý các gói tin
        không hoàn chỉnh đến từ `raw_data`.

        Nó nên trả về một generator (sử dụng `yield`). Mỗi lần `yield`, nó
        trả về một đối tượng `SensorData` đã được giải mã và chuẩn hóa hoàn chỉnh.
        Một khối `raw_data` có thể chứa 0, 1 hoặc nhiều gói tin hoàn chỉnh,
        do đó generator này có thể yield 0, 1 hoặc nhiều lần cho mỗi lần gọi.

        Returns:
            Generator[SensorData, None, None]: Một generator trả về các đối tượng SensorData.
        """
        pass
        # Ví dụ đơn giản (sẽ được implement trong lớp con):
        # self.internal_buffer.extend(raw_data)
        # while complete_packet := self._find_complete_packet_in_buffer():
        #     parsed_values, timestamp_info = self._parse_packet(complete_packet)
        #     unix_timestamp = self._calculate_unix_timestamp(timestamp_info)
        #     yield SensorData(
        #         timestamp=unix_timestamp,
        #         sensor_id=self.sensor_id,
        #         data_type='imu', # Hoặc lấy từ config
        #         values=parsed_values,
        #         raw_timestamp=timestamp_info.get('raw'),
        #         units=self._get_units() # Lấy đơn vị từ config hoặc hardcode
        #     )
        #     self._remove_packet_from_buffer()