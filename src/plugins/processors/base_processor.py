# src/plugins/processors/base_processor.py
from abc import ABC, abstractmethod
from typing import Any, Generator, Dict
from src.data.models import SensorData # Thường thì processor sẽ xử lý SensorData

class BaseProcessor(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các bộ xử lý dữ liệu (Processors).

    Processors nhận dữ liệu đã được chuẩn hóa (thường là SensorData) từ Decoder
    hoặc từ một Processor khác, thực hiện một phép biến đổi hoặc phân tích,
    và trả về kết quả.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo Processor với cấu hình cụ thể.

        Args:
            config (Dict[str, Any]): Dictionary chứa các tham số cấu hình
                                     cho Processor này (ví dụ: 'cutoff_freq',
                                     'window_size', 'target_channels').
        """
        self.config = config
        print(f"Initializing {self.__class__.__name__} with config: {config}")

    @abstractmethod
    def process(self, data: Any) -> Generator[Any, None, None]:
        """
        Phương thức cốt lõi để xử lý dữ liệu.

        Phương thức này PHẢI được triển khai bởi các lớp con.
        Nó nhận một đơn vị dữ liệu đầu vào (thường là `SensorData`).
        Nó nên trả về một generator (sử dụng `yield`). Mỗi lần `yield`, nó
        trả về một đơn vị dữ liệu kết quả sau khi xử lý.
        Một Processor có thể:
        - Trả về dữ liệu đã sửa đổi (yield 1 lần).
        - Không trả về gì cả (không yield) nếu dữ liệu bị lọc bỏ.
        - Trả về nhiều kết quả mới (yield nhiều lần).
        - Thay đổi kiểu dữ liệu trả về (ví dụ: từ SensorData sang một kiểu kết quả phân tích khác).

        Args:
            data (Any): Dữ liệu đầu vào, thường là một đối tượng SensorData.

        Returns:
            Generator[Any, None, None]: Một generator trả về (các) kết quả xử lý.
        """
        pass
        # Ví dụ đơn giản (sẽ được implement trong lớp con):
        # if isinstance(data, SensorData) and 'accX' in data.values:
        #     processed_value = data.values['accX'] * 2 # Ví dụ xử lý
        #     data.values['processedAccX'] = processed_value
        #     data.units['processedAccX'] = data.get_unit('accX')
        #     yield data # Trả về đối tượng SensorData đã sửa đổi