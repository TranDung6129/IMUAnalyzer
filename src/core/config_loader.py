# Cấu trúc đề xuất
class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        
    def load(self):
        # Đọc file YAML/JSON
        # Xác thực schema
        # Trả về dict cấu hình
        pass
    
    def validate(self, config_dict):
        # Xác thực cấu hình
        # TODO: Implement validation logic
        pass