from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QTabWidget, QLabel, QPushButton, QSplitter)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal

from src.ui.visualizers.time_series_plot import TimeSeriesPlot
from src.ui.visualizers.fft_plot import FFTPlot
from src.ui.visualizers.orientation_3d import Orientation3D

class Dashboard(QWidget):
    """Widget that contains and manages multiple visualization widgets."""
    
    def __init__(self, parent=None):
        """Initialize the dashboard widget."""
        super().__init__(parent)

        # Store visualizer widgets
        self.visualizers = {}

        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        
        # Create default tabs
        self._create_time_series_tab()
        self._create_fft_tab()
        self._create_3d_tab()
        
        # Add to layout
        main_layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add tab buttons
        self.add_time_series_btn = QPushButton("Add Time Series")
        button_layout.addWidget(self.add_time_series_btn)
        
        self.add_fft_btn = QPushButton("Add FFT")
        button_layout.addWidget(self.add_fft_btn)
        
        self.add_3d_btn = QPushButton("Add 3D View")
        button_layout.addWidget(self.add_3d_btn)
        
        # Add stretch to push buttons to the left
        button_layout.addStretch(1)
        
        # Add button layout
        main_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Tab buttons
        self.add_time_series_btn.clicked.connect(self._on_add_time_series)
        self.add_fft_btn.clicked.connect(self._on_add_fft)
        self.add_3d_btn.clicked.connect(self._on_add_3d)
        
        # Tab closing
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
    
    def _create_time_series_tab(self):
        """Create a new time series tab."""
        # Create time series widget
        time_series = TimeSeriesPlot()
        
        # Add to tabs
        tab_index = self.tab_widget.addTab(time_series, "Time Series")
        
        # Store reference
        widget_id = f"time_series_{tab_index}"
        self.visualizers[widget_id] = time_series
        
        return time_series
    
    def _create_fft_tab(self):
        """Create a new FFT tab."""
        # Create FFT widget
        fft_plot = FFTPlot()
        
        # Add to tabs
        tab_index = self.tab_widget.addTab(fft_plot, "FFT")
        
        # Store reference
        widget_id = f"fft_{tab_index}"
        self.visualizers[widget_id] = fft_plot
        
        return fft_plot
    
    def _create_3d_tab(self):
        """Create a new 3D orientation tab."""
        # Create 3D widget
        orientation_3d = Orientation3D()
        
        # Add to tabs
        tab_index = self.tab_widget.addTab(orientation_3d, "3D Orientation")
        
        # Store reference
        widget_id = f"3d_{tab_index}"
        self.visualizers[widget_id] = orientation_3d
        
        return orientation_3d
    
    @pyqtSlot()
    def _on_add_time_series(self):
        """Handle add time series button click."""
        time_series = self._create_time_series_tab()
        self.tab_widget.setCurrentWidget(time_series)
    
    @pyqtSlot()
    def _on_add_fft(self):
        """Handle add FFT button click."""
        fft_plot = self._create_fft_tab()
        self.tab_widget.setCurrentWidget(fft_plot)
    
    @pyqtSlot()
    def _on_add_3d(self):
        """Handle add 3D view button click."""
        orientation_3d = self._create_3d_tab()
        self.tab_widget.setCurrentWidget(orientation_3d)
    
    @pyqtSlot(int)
    def _on_tab_close_requested(self, index):
        """Handle tab close request."""
        # Don't allow closing the last tab
        if self.tab_widget.count() <= 1:
            return
        
        # Get the widget at the index
        widget = self.tab_widget.widget(index)
        
        # Remove widget reference
        for widget_id, visualizer in list(self.visualizers.items()):
            if visualizer == widget:
                del self.visualizers[widget_id]
                break
        
        # Remove tab
        self.tab_widget.removeTab(index)
        
        # Delete the widget
        widget.deleteLater()
    
    def update_time_series(self, channel_name, timestamp, value):
        """Update all time series plots with new data."""
        for widget_id, widget in self.visualizers.items():
            if widget_id.startswith("time_series_") and isinstance(widget, TimeSeriesPlot):
                widget.update_data(channel_name, timestamp, value)
    
    def update_fft(self, channel_name, frequencies, amplitudes, units=None):
        """Update all FFT plots with new data."""
        for widget_id, widget in self.visualizers.items():
            if widget_id.startswith("fft_") and isinstance(widget, FFTPlot):
                widget.update_data(channel_name, frequencies, amplitudes, units)
    
    def update_orientation(self, roll, pitch, yaw):
        """Update all 3D orientation visualizers with new data."""
        for widget_id, widget in self.visualizers.items():
            if widget_id.startswith("3d_") and isinstance(widget, Orientation3D):
                widget.update_orientation(roll, pitch, yaw)