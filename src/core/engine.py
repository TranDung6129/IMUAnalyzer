# Cấu trúc đề xuất
class Engine:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.plugin_manager = None
        self.pipelines = []
        
    def setup(self):
        # Tải cấu hình
        # Khởi tạo plugin manager
        # Tạo các pipeline dựa trên cấu hình
        pass

    def run(self):
        # Chạy tất cả các pipeline
        pass

    def stop(self):
        # Dừng tất cả các pipeline
        pass