# Cấu trúc đề xuất
class Pipeline:
    def __init__(self, reader, decoder, processors=None, visualizers=None):
        self.reader = reader
        self.decoder = decoder
        self.processors = processors or []
        self.visualizers = visualizers or []
        self.running = False
        
    def run(self):
        # Chạy toàn bộ pipeline cho đến khi hết dữ liệu
        pass

    def run_step(self):
        # Thực hiện một bước (đọc → giải mã → xử lý → hiển thị)
        pass

    def stop(self):
        # Dừng pipeline
        pass