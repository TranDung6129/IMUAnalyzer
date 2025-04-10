from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QCheckBox
from PyQt6.QtCore import Qt, pyqtSlot
import pyqtgraph as pg
import numpy as np

class FFTPlot(QWidget):
    """Widget for displaying frequency-domain (FFT) data."""
    
    def __init__(self, parent=None):
        """Initialize the FFT plot widget."""
        super().__init__(parent)
        
        # Data storage
        self.data = {}  # {channel_name: {'f': np.array, 'amplitude': np.array}}
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
        self.plot_widget.setLabel("bottom", "Frequency", "Hz")
        self.plot_widget.setLabel("left", "Amplitude")
        self.plot_widget.addLegend()
        
        # Set logarithmic X scale (for frequency)
        self.plot_widget.setLogMode(x=True, y=False)
        
        # Add to layout
        main_layout.addWidget(self.plot_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Auto-range checkbox
        self.auto_range_cb = QCheckBox("Auto Range")
        self.auto_range_cb.setChecked(True)
        self.auto_range_cb.toggled.connect(self._on_auto_range_toggled)
        controls_layout.addWidget(self.auto_range_cb)
        
        # Scale selector
        controls_layout.addWidget(QLabel("Scale:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Linear", "Log"])
        self.scale_combo.currentTextChanged.connect(self._on_scale_changed)
        controls_layout.addWidget(self.scale_combo)
        
        # Add stretch to push controls to the left
        controls_layout.addStretch(1)
        
        # Add controls to main layout
        main_layout.addLayout(controls_layout)
    
    def add_channel(self, channel_name, units=None):
        """Add a new data channel to the plot."""
        if channel_name in self.curves:
            return
        
        # Initialize data
        self.data[channel_name] = {
            "f": np.array([]),
            "amplitude": np.array([])
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
        if channel_name in self.data:
            self.data[channel_name]["f"] = np.array([])
            self.data[channel_name]["amplitude"] = np.array([])
            self.curves[channel_name].setData([], [])
    
    def clear_all(self):
        """Clear all data from the plot."""
        for channel in self.data:
            self.clear_channel(channel)
    
    def update_data(self, channel_name, frequencies, amplitudes, units=None):
        """Update the plot with new FFT data."""
        if channel_name not in self.data:
            self.add_channel(channel_name, units)
        
        # Update data
        self.data[channel_name]["f"] = np.array(frequencies)
        self.data[channel_name]["amplitude"] = np.array(amplitudes)
        
        # Update plot
        self.curves[channel_name].setData(
            self.data[channel_name]["f"],
            self.data[channel_name]["amplitude"]
        )
    
    @pyqtSlot(bool)
    def _on_auto_range_toggled(self, checked):
        """Handle auto-range checkbox toggle."""
        self.plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=checked)
    
    @pyqtSlot(str)
    def _on_scale_changed(self, text):
        """Handle scale type change."""
        if text == "Log":
            self.plot_widget.setLogMode(x=True, y=True)
        else:
            self.plot_widget.setLogMode(x=True, y=False)