# src/data/models.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time

@dataclass
class SensorData:
    """
    Cấu trúc dữ liệu chuẩn cho dữ liệu cảm biến sau khi được giải mã.

    Attributes:
        timestamp (float): Dấu thời gian chuẩn hóa dưới dạng UNIX timestamp (số giây float kể từ epoch).
                           Đây là trường thời gian chính được sử dụng bên trong hệ thống.
        sensor_id (str): Định danh duy nhất cho cảm biến hoặc nguồn dữ liệu.
        data_type (str): Loại dữ liệu chính (ví dụ: 'imu', 'gps', 'image', 'temperature').
        values (Dict[str, Any]): Từ điển chứa các giá trị dữ liệu thực tế.
                                 Keys là tên của các kênh dữ liệu (ví dụ: 'accX', 'gyroY', 'latitude').
                                 Values là giá trị tương ứng.
        raw_timestamp (Optional[Any]): Dấu thời gian gốc từ cảm biến hoặc nguồn dữ liệu (nếu có).
                                      Có thể là chuỗi, số nguyên, hoặc đối tượng datetime.
                                      Hữu ích cho việc gỡ lỗi hoặc tham chiếu.
        units (Dict[str, str]): Từ điển chứa đơn vị cho từng giá trị trong trường 'values'.
                                Keys khớp với keys trong 'values'.
                                Values là chuỗi biểu diễn đơn vị (ví dụ: 'm/s²', 'deg/s', 'deg').
                                Quan trọng cho việc xử lý và hiển thị nhất quán.
        metadata (Dict[str, Any]): (Tùy chọn) Từ điển chứa các siêu dữ liệu bổ sung nếu cần.
    """
    timestamp: float
    sensor_id: str
    data_type: str
    values: Dict[str, Any] = field(default_factory=dict)
    raw_timestamp: Optional[Any] = None
    units: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict) 

    def __post_init__(self):
        # Thực hiện kiểm tra hoặc chuyển đổi cơ bản nếu cần sau khi khởi tạo
        # Ví dụ: đảm bảo timestamp là float
        if not isinstance(self.timestamp, float):
            try:
                # Cố gắng chuyển đổi timestamp sang float
                self.timestamp = float(self.timestamp)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert timestamp {self.timestamp} for sensor {self.sensor_id} to float. Using current time.")
                # Cung cấp giá trị mặc định hoặc ghi log lỗi nghiêm trọng hơn
                self.timestamp = time.time()

    def get_value(self, key: str, default: Any = None) -> Any:
        """Lấy giá trị từ trường 'values' một cách an toàn."""
        return self.values.get(key, default)

    def get_unit(self, key: str, default: str = "") -> str:
        """Lấy đơn vị cho một giá trị cụ thể."""
        return self.units.get(key, default)