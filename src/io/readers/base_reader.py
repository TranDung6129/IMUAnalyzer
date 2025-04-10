# src/io/readers/base_reader.py
from abc import ABC, abstractmethod
from typing import Any, Generator, Dict

class BaseReader(ABC):
    """
    Lớp cơ sở trừu tượng (Abstract Base Class) cho tất cả các bộ đọc dữ liệu (Readers).

    Readers chịu trách nhiệm đọc dữ liệu THÔ (raw data) từ một nguồn cụ thể
    (ví dụ: file, cổng serial, network stream) và cung cấp nó cho Decoder.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo Reader với cấu hình cụ thể được cung cấp từ file config.

        Args:
            config (Dict[str, Any]): Dictionary chứa các tham số cấu hình
                                     cho Reader này (ví dụ: 'file_path', 'port', 'baudrate').
        """
        self.config = config
        print(f"Initializing {self.__class__.__name__} with config: {config}") # Log cơ bản

    @abstractmethod
    def read(self) -> Generator[bytes, None, None]:
        """
        Phương thức cốt lõi để đọc dữ liệu thô từ nguồn.

        Phương thức này PHẢI được triển khai bởi các lớp con.
        Nó nên trả về một generator (sử dụng `yield`).
        Mỗi lần `yield`, nó sẽ trả về một khối dữ liệu thô dưới dạng `bytes`.

        - Đối với nguồn real-time (serial, network): yield dữ liệu ngay khi có.
        - Đối với nguồn file (post-processing): yield dữ liệu theo từng chunk.

        Generator nên kết thúc (return hoặc raise StopIteration) khi không còn dữ liệu.

        Returns:
            Generator[bytes, None, None]: Một generator trả về các khối dữ liệu bytes.
        """
        pass
        # Ví dụ đơn giản (sẽ được implement trong lớp con):
        # with open(self.config['file_path'], 'rb') as f:
        #     while chunk := f.read(4096):
        #         yield chunk

    def open(self):
        """
        (Tùy chọn) Phương thức để thiết lập hoặc mở kết nối/tài nguyên.
        Ví dụ: Mở file, kết nối cổng serial.
        Thường được gọi khi sử dụng với câu lệnh `with`.
        """
        # print(f"Opening reader {self.__class__.__name__}")
        pass

    def close(self):
        """
        (Tùy chọn) Phương thức để đóng kết nối hoặc giải phóng tài nguyên.
        Ví dụ: Đóng file, đóng cổng serial.
        Thường được gọi khi kết thúc câu lệnh `with` hoặc khi pipeline dừng.
        """
        # print(f"Closing reader {self.__class__.__name__}")
        pass

    def __enter__(self):
        """Hỗ trợ context manager (câu lệnh `with`)."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Hỗ trợ context manager (câu lệnh `with`). Đảm bảo close được gọi."""
        self.close()

    def get_status(self) -> Dict[str, Any]:
        """(Tùy chọn) Trả về trạng thái hiện tại của reader (ví dụ: connected, error)."""
        return {"status": "unknown"}