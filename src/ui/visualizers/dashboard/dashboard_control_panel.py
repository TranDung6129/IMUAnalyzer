"""
Control panel for the grid dashboard.
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QComboBox, 
                             QFileDialog, QLabel, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt

from src.ui.visualizers.time_series_plot import TimeSeriesPlot
from src.ui.visualizers.fft_plot import FFTPlot
from src.ui.visualizers.orientation_3d import Orientation3D
from src.ui.visualizers.dashboard.dashboard_manager import DashboardManager
import os

class DashboardControlPanel(QWidget):
    """Control panel for grid dashboard actions."""
    
    def __init__(self, dashboard_panel, parent=None):
        """Initialize dashboard control panel."""
        super().__init__(parent)
        
        # Store references
        self.dashboard_panel = dashboard_panel
        self.dashboard_manager = DashboardManager(dashboard_panel)
        
        # UI setup
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()

    def setup_ui(self):
        """Thiết lập các thành phần giao diện người dùng."""
        # Layout chính
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Nút thêm biểu đồ chuỗi thời gian
        self.add_timeseries_btn = QPushButton("Thêm Time Series")
        layout.addWidget(self.add_timeseries_btn)
        
        # Nút thêm biểu đồ FFT
        self.add_fft_btn = QPushButton("Thêm FFT")
        layout.addWidget(self.add_fft_btn)
        
        # Nút thêm biểu đồ 3D
        self.add_3d_btn = QPushButton("Thêm 3D View")
        layout.addWidget(self.add_3d_btn)
        
        # Dấu phân cách
        layout.addSpacing(20)
        
        # Các nút quản lý layout
        self.save_layout_btn = QPushButton("Lưu Layout")
        layout.addWidget(self.save_layout_btn)
        
        self.load_layout_btn = QPushButton("Tải Layout")
        layout.addWidget(self.load_layout_btn)

        self.clear_all_btn = QPushButton("Xóa tất cả")
        layout.addWidget(self.clear_all_btn)

        self.remove_widget_btn = QPushButton("Xóa widget đã chọn")
        self.remove_widget_btn.setStyleSheet("background-color: #ffcccc;")  # Màu đỏ nhạt
        layout.addWidget(self.remove_widget_btn)


        # Thêm khoảng trống để đẩy các nút về bên trái
        layout.addStretch(1)

    def connect_signals(self):
        """Kết nối các tín hiệu với slots."""
        # Kết nối các nút thêm biểu đồ
        self.add_timeseries_btn.clicked.connect(self._on_add_timeseries)
        self.add_fft_btn.clicked.connect(self._on_add_fft)
        self.add_3d_btn.clicked.connect(self._on_add_3d)
        
        # Kết nối các nút quản lý layout
        self.save_layout_btn.clicked.connect(self._on_save_layout)
        self.load_layout_btn.clicked.connect(self._on_load_layout)

        # Kết nối nút xóa widget đã chọn
        # Kết nối tín hiệu
        self.remove_widget_btn.clicked.connect(self._on_remove_selected_widget)
        self.clear_all_btn.clicked.connect(self._on_clear_all)
        
    def _on_add_timeseries(self):
        """Xử lý khi nhấn nút thêm biểu đồ chuỗi thời gian."""
        # Tạo widget time series
        time_series = TimeSeriesPlot()
        
        # Thêm vào dashboard
        widget_id = f"timeseries_{len(self.dashboard_panel.widgets) + 1}"
        self.dashboard_panel.add_widget(time_series, "Time Series", widget_id)

    def _on_add_fft(self):
        """Xử lý khi nhấn nút thêm biểu đồ FFT."""
        # Tạo widget FFT
        fft_plot = FFTPlot()
        
        # Thêm vào dashboard
        widget_id = f"fft_{len(self.dashboard_panel.widgets) + 1}"
        self.dashboard_panel.add_widget(fft_plot, "FFT Plot", widget_id)

    def _on_add_3d(self):
        """Xử lý khi nhấn nút thêm biểu đồ 3D."""
        # Tạo widget 3D
        orientation_3d = Orientation3D()
        
        # Thêm vào dashboard
        widget_id = f"3d_{len(self.dashboard_panel.widgets) + 1}"
        self.dashboard_panel.add_widget(orientation_3d, "3D Orientation", widget_id)

    def _on_save_layout(self):
        """Xử lý khi nhấn nút lưu layout."""
        # Hiển thị hộp thoại chọn file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Layout Dashboard", "", "Layout Files (*.json)"
        )
        
        if file_path:
            # Lưu layout sử dụng dashboard manager
            self.dashboard_manager.save_layout(file_path)

    def _on_load_layout(self):
        """Xử lý khi nhấn nút tải layout."""
        # Hiển thị hộp thoại chọn file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Tải Layout Dashboard", "", "Layout Files (*.json)"
        )
        
        if file_path and os.path.exists(file_path):
            # Tải layout sử dụng dashboard manager
            self.dashboard_manager.load_layout(file_path)


    #  Xử lý xóa widget đã chọn
    def _on_remove_selected_widget(self):
        """Xử lý khi nút xóa widget được nhấn."""
        # Sửa từ _get_selected_widget_id() thành dashboard_panel.get_selected_widget_id()
        selected_id = self.dashboard_panel.get_selected_widget_id()
        
        if selected_id:
            # Xác nhận trước khi xóa
            reply = QMessageBox.question(
                self, 
                "Xác nhận", 
                "Bạn có chắc muốn xóa widget này không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.dashboard_panel.remove_widget(selected_id)
        else:
            QMessageBox.information(self, "Thông báo", "Chưa có widget nào được chọn")
    
    def _on_clear_all(self):
        """Xóa tất cả widgets."""
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self, 
            'Xác nhận xóa', 
            'Bạn có chắc chắn muốn xóa tất cả widgets?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.dashboard_panel.clear_all()