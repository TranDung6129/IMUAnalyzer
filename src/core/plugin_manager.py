# Cấu trúc đề xuất
class PluginManager:
    def __init__(self, plugin_dirs=None):
        self.plugin_dirs = plugin_dirs or ["src/plugins"]
        self.discovered_plugins = {}
        
    def discover_plugins(self):
        # Quét thư mục plugin để tìm các lớp plugin
        pass
    
    def load_plugin(self, plugin_type, plugin_name):
        # Tìm và tải plugin dựa trên loại và tên
        # Trả về lớp plugin (chưa khởi tạo)
        print(f"Loading plugin: type={plugin_type}, name={plugin_name}")
        # Add actual implementation here
        pass
        
    def create_plugin_instance(self, plugin_type, plugin_name, config):
        # Tạo instance của plugin với cấu hình
        pass 