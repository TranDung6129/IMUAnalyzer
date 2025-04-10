from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Dict, List, Any, Callable

class DataBridge(QObject):
    """Bridge for data transfer between core engine and UI components."""
    
    # Custom signals
    sensor_data_received = pyqtSignal(dict)  # Emitted when new sensor data is received
    fft_data_received = pyqtSignal(dict)     # Emitted when new FFT data is received
    orientation_data_received = pyqtSignal(float, float, float)  # roll, pitch, yaw
    
    def __init__(self, parent=None):
        """Initialize the data bridge."""
        super().__init__(parent)
        
        # Registered visualizers
        self.visualizers = {}
    
    def register_visualizer(self, visualizer_id, visualizer):
        """
        Register a visualizer to receive data.
        
        Args:
            visualizer_id: Unique identifier for the visualizer
            visualizer: Visualizer object
        """
        self.visualizers[visualizer_id] = visualizer
    
    # Thêm phương thức mới
    def register_grid_visualizer(self, widget_id, visualizer_type, visualizer):
        """
        Đăng ký một visualizer trong grid dashboard.
        
        Args:
            widget_id: ID duy nhất của widget trong grid
            visualizer_type: Loại visualizer (time_series, fft, orientation_3d, etc.)
            visualizer: Object visualizer
        """
        widget_key = f"{visualizer_type}_{widget_id}"
        self.visualizers[widget_key] = visualizer

    def unregister_visualizer(self, visualizer_id):
        """
        Unregister a visualizer.
        
        Args:
            visualizer_id: Identifier of the visualizer to unregister
        """
        if visualizer_id in self.visualizers:
            del self.visualizers[visualizer_id]
    
    @pyqtSlot(dict)
    def process_data(self, data_dict):
        """
        Process data from the engine and forward to appropriate visualizers.
        
        Args:
            data_dict: Dictionary containing data and metadata
        """
        if not isinstance(data_dict, dict) or "data" not in data_dict:
            return
        
        data = data_dict["data"]
        
        # Check data type and emit appropriate signal
        if hasattr(data, "data_type"):
            if data.data_type == "accelerometer":
                self._process_sensor_data(data)
            elif data.data_type == "gyroscope":
                self._process_sensor_data(data)
            elif data.data_type == "magnetometer":
                self._process_sensor_data(data)
            elif data.data_type == "fft":
                self._process_fft_data(data)
            elif data.data_type == "angle":
                self._process_orientation_data(data)
    
    def _process_sensor_data(self, data):
        """
        Process sensor data.
        
        Args:
            data: SensorData object
        """
        # Create data dictionary
        sensor_data = {
            "sensor_id": data.sensor_id,
            "data_type": data.data_type,
            "timestamp": data.timestamp,
            "values": data.values,
            "units": data.units
        }
        
        # Emit signal
        self.sensor_data_received.emit(sensor_data)
    
    def _process_fft_data(self, data):
        """
        Process FFT data.
        
        Args:
            data: SensorData object with FFT data
        """
        # Create data dictionary
        fft_data = {
            "sensor_id": data.sensor_id,
            "data_type": data.data_type,
            "timestamp": data.timestamp,
            "values": data.values,
            "frequencies": data.metadata.get("frequencies", []),
            "units": data.units
        }
        
        # Emit signal
        self.fft_data_received.emit(fft_data)
    
    def _process_orientation_data(self, data):
        """
        Process orientation data.
        
        Args:
            data: SensorData object with orientation data
        """
        # Extract Euler angles
        roll = data.values.get("roll", 0.0)
        pitch = data.values.get("pitch", 0.0)
        yaw = data.values.get("yaw", 0.0)
        
        # Emit signal
        self.orientation_data_received.emit(roll, pitch, yaw)