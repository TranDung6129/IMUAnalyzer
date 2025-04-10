from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QCheckBox
from PyQt6.QtCore import Qt, pyqtSlot
import pyqtgraph as pg
import numpy as np
from collections import deque
import time

class TimeSeriesPlot(QWidget):
    """Widget for displaying time series data."""
    
    def __init__(self, parent=None, max_points=1000):
        """Initialize the time series plot widget."""
        super().__init__(parent)
        
        # Data storage
        self.max_points = max_points
        self.data_buffers = {}  # {channel_name: {'x': deque, 'y': deque}}
        self.curves = {}  # {channel_name: PlotCurveItem}
        self.colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128)   # Purple
        ]
        self.color_index = 0
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel("bottom", "Time", "s")
        self.plot_widget.setLabel("left", "Value")
        self.plot_widget.addLegend()
        
        # Add to layout
        main_layout.addWidget(self.plot_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Auto-range checkbox
        self.auto_range_cb = QCheckBox("Auto Range")
        self.auto_range_cb.setChecked(True)
        self.auto_range_cb.toggled.connect(self._on_auto_range_toggled)
        controls_layout.addWidget(self.auto_range_cb)
        
        # Time window control
        controls_layout.addWidget(QLabel("Time Window:"))
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems(["10s", "30s", "1m", "5m", "All"])
        self.time_window_combo.currentTextChanged.connect(self._on_time_window_changed)
        controls_layout.addWidget(self.time_window_combo)
        
        # Add stretch to push controls to the left
        controls_layout.addStretch(1)
        
        # Add controls to main layout
        main_layout.addLayout(controls_layout)
    
    def add_channel(self, channel_name, units=None):
        """Add a new data channel to the plot."""
        if channel_name in self.curves:
            return
        
        # Create data buffers
        self.data_buffers[channel_name] = {
            "x": deque(maxlen=self.max_points),
            "y": deque(maxlen=self.max_points)
        }
        
        # Choose color
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        
        # Create curve
        pen = pg.mkPen(color=color, width=2)
        self.curves[channel_name] = self.plot_widget.plot(
            pen=pen,
            name=f"{channel_name}" + (f" ({units})" if units else "")
        )
    
    def clear_channel(self, channel_name):
        """Clear data for a specific channel."""
        if channel_name in self.data_buffers:
            self.data_buffers[channel_name]["x"].clear()
            self.data_buffers[channel_name]["y"].clear()
            self.curves[channel_name].setData([], [])
    
    def clear_all(self):
        """Clear all data from the plot."""
        for channel in self.data_buffers:
            self.clear_channel(channel)
    
    def update_data(self, channel_name, timestamp, value):
        """Update the plot with new data."""
        if channel_name not in self.data_buffers:
            self.add_channel(channel_name)
        
        # Add data to buffers
        self.data_buffers[channel_name]["x"].append(timestamp)
        self.data_buffers[channel_name]["y"].append(value)
        
        # Update plot
        self._update_plot(channel_name)
    
    def update_batch(self, data_dict):
        """Update multiple channels with new data."""
        # data_dict = {channel_name: (timestamp, value), ...}
        for channel_name, (timestamp, value) in data_dict.items():
            if channel_name not in self.data_buffers:
                self.add_channel(channel_name)
            
            # Add data to buffers
            self.data_buffers[channel_name]["x"].append(timestamp)
            self.data_buffers[channel_name]["y"].append(value)
        
        # Update all plots
        for channel_name in data_dict:
            self._update_plot(channel_name)
    
    def _update_plot(self, channel_name):
        """Update the plot for a specific channel."""
        if channel_name in self.curves and channel_name in self.data_buffers:
            # Get data arrays
            x = list(self.data_buffers[channel_name]["x"])
            y = list(self.data_buffers[channel_name]["y"])
            
            # Apply time window if needed
            time_window = self._get_time_window()
            if time_window > 0 and x:
                current_time = x[-1]
                min_time = current_time - time_window
                
                # Find index of first point within time window
                start_idx = 0
                for i, t in enumerate(x):
                    if t >= min_time:
                        start_idx = i
                        break
                
                # Slice arrays
                x = x[start_idx:]
                y = y[start_idx:]
            
            # Update curve
            self.curves[channel_name].setData(x, y)
    
    def _get_time_window(self):
        """Get the current time window in seconds."""
        text = self.time_window_combo.currentText()
        
        if text == "All":
            return 0
        
        # Parse time window string
        if text.endswith("s"):
            return int(text[:-1])
        elif text.endswith("m"):
            return int(text[:-1]) * 60
        
        return 0
    
    @pyqtSlot(bool)
    def _on_auto_range_toggled(self, checked):
        """Handle auto-range checkbox toggle."""
        self.plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=checked)
    
    @pyqtSlot(str)
    def _on_time_window_changed(self, text):
        """Handle time window change."""
        # Update all channels
        for channel_name in self.data_buffers:
            self._update_plot(channel_name)