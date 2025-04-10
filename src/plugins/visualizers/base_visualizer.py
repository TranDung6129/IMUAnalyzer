# src/plugins/visualizers/base_visualizer.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from src.data.models import SensorData # Thường thì visualizer sẽ hiển thị SensorData

class BaseVisualizer(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các bộ hiển thị dữ liệu (Visualizers).

    Visualizers nhận dữ liệu (thường là SensorData hoặc kết quả từ Processor)
    và hiển thị nó cho người dùng (ví dụ: vẽ đồ thị, in ra console, cập nhật GUI).
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo Visualizer với cấu hình cụ thể.

        Args:
            config (Dict[str, Any]): Dictionary chứa các tham số cấu hình
                                     cho Visualizer này (ví dụ: 'output_dir',
                                     'plot_title', 'update_interval').
        """
        self.config = config
        print(f"Initializing {self.__class__.__name__} with config: {config}")

    @abstractmethod
    def visualize(self, data: Any) -> None:
        """
        Phương thức cốt lõi để hiển thị dữ liệu.

        Phương thức này PHẢI được triển khai bởi các lớp con.
        Nó nhận một đơn vị dữ liệu đầu vào.
        Nhiệm vụ của nó là thực hiện hành động hiển thị. Nó không trả về giá trị.

        - Đối với real-time: Phương thức này có thể được gọi liên tục để cập nhật hiển thị.
        - Đối với post-processing: Có thể được gọi một lần cho mỗi kết quả hoặc
          tích lũy dữ liệu và hiển thị ở cuối (trong `teardown`).

        Args:
            data (Any): Dữ liệu cần hiển thị.
        """
        pass
        # Ví dụ đơn giản (sẽ được implement trong lớp con):
        # if isinstance(data, SensorData):
        #     ts = data.timestamp
        #     val = data.get_value('accX')
        #     if val is not None:
        #         print(f"[{ts:.3f}] Sensor '{data.sensor_id}': accX = {val:.4f} {data.get_unit('accX')}")

    def setup(self):
        """
        (Tùy chọn) Thực hiện các thiết lập ban đầu cần thiết cho việc hiển thị.
        Ví dụ: Tạo cửa sổ plot, khởi tạo thư viện GUI.
        Thường được gọi một lần trước khi pipeline bắt đầu xử lý dữ liệu.
        """
        # print(f"Setting up visualizer {self.__class__.__name__}")
        pass

    def teardown(self):
        """
        (Tùy chọn) Thực hiện các hành động dọn dẹp sau khi hiển thị kết thúc.
        Ví dụ: Lưu plot cuối cùng, đóng cửa sổ, giải phóng tài nguyên GUI.
        Thường được gọi một lần sau khi pipeline xử lý xong tất cả dữ liệu.
        """
        # print(f"Tearing down visualizer {self.__class__.__name__}")
        pass