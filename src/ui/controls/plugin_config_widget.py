from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QComboBox, QPushButton, QLineEdit,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QTreeView,
                             QGroupBox, QTabWidget, QSplitter, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSettings, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import yaml

class PluginConfigWidget(QWidget):
    """Widget for configuring pipeline plugins."""
    
    # Custom signals
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize the plugin configuration widget."""
        super().__init__(parent)
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Current configuration
        self.current_config = {}
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create tabs for different plugin types
        self.tab_widget = QTabWidget()
        
        # Create tab for each plugin type
        self.reader_tab = self._create_plugin_tab("Reader")
        self.decoder_tab = self._create_plugin_tab("Decoder")
        self.processors_tab = self._create_plugin_tab("Processors")
        self.visualizers_tab = self._create_plugin_tab("Visualizers")
        
        self.tab_widget.addTab(self.reader_tab, "Reader")
        self.tab_widget.addTab(self.decoder_tab, "Decoder")
        self.tab_widget.addTab(self.processors_tab, "Processors")
        self.tab_widget.addTab(self.visualizers_tab, "Visualizers")
        
        # Add tabs to layout
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply")
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset")
        button_layout.addWidget(self.reset_btn)
        
        # Add buttons to layout
        main_layout.addLayout(button_layout)
    
    def _create_plugin_tab(self, plugin_type):
        """Create a tab for a specific plugin type."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Plugin type selector (if needed)
        if plugin_type in ["Reader", "Decoder"]:
            # Single plugin selection
            type_layout = QFormLayout()
            
            type_label = QLabel(f"{plugin_type} Type:")
            type_combo = QComboBox()
            type_combo.setObjectName(f"{plugin_type.lower()}_type")
            
            # Add placeholder items (will be populated later)
            if plugin_type == "Reader":
                type_combo.addItems(["FileReader", "SerialReader"])
            elif plugin_type == "Decoder":
                type_combo.addItems(["WitMotionDecoder"])
            
            type_layout.addRow(type_label, type_combo)
            layout.addLayout(type_layout)
        else:
            # Multiple plugin management
            type_layout = QHBoxLayout()
            
            type_label = QLabel(f"{plugin_type} Type:")
            type_combo = QComboBox()
            type_combo.setObjectName(f"{plugin_type.lower()}_type")
            
            # Add placeholder items (will be populated later)
            if plugin_type == "Processors":
                type_combo.addItems(["LowPassFilterProcessor", "FFTProcessor", "IntegrationProcessor"])
            elif plugin_type == "Visualizers":
                type_combo.addItems(["TimeSeriesVisualizer", "ConsoleVisualizer"])
            
            type_layout.addWidget(type_label)
            type_layout.addWidget(type_combo)
            
            add_btn = QPushButton("Add")
            add_btn.setObjectName(f"add_{plugin_type.lower()}")
            type_layout.addWidget(add_btn)
            
            layout.addLayout(type_layout)
            
            # List of added plugins
            list_group = QGroupBox(f"Current {plugin_type}")
            list_layout = QVBoxLayout()
            list_group.setLayout(list_layout)
            
            plugin_list = QTreeView()
            plugin_list.setObjectName(f"{plugin_type.lower()}_list")
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Type", ""])
            plugin_list.setModel(model)
            
            list_layout.addWidget(plugin_list)
            
            # Remove button
            remove_btn = QPushButton("Remove Selected")
            remove_btn.setObjectName(f"remove_{plugin_type.lower()}")
            list_layout.addWidget(remove_btn)
            
            layout.addWidget(list_group)
        
        # Configuration group
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout()
        config_group.setLayout(config_layout)
        
        # Add configuration fields based on plugin type
        if plugin_type == "Reader":
            # FileReader fields
            self._add_file_reader_fields(config_layout)
            
            # SerialReader fields
            self._add_serial_reader_fields(config_layout)
        elif plugin_type == "Decoder":
            # Common Decoder fields
            sensor_id_edit = QLineEdit()
            sensor_id_edit.setObjectName("decoder_sensor_id")
            config_layout.addRow("Sensor ID:", sensor_id_edit)
            
            # WitMotion fields
            acc_range = QDoubleSpinBox()
            acc_range.setObjectName("decoder_acc_range")
            acc_range.setRange(2.0, 16.0)
            acc_range.setValue(16.0)
            acc_range.setSingleStep(2.0)
            config_layout.addRow("Acc Range (g):", acc_range)
            
            gyro_range = QDoubleSpinBox()
            gyro_range.setObjectName("decoder_gyro_range")
            gyro_range.setRange(250.0, 2000.0)
            gyro_range.setValue(2000.0)
            gyro_range.setSingleStep(250.0)
            config_layout.addRow("Gyro Range (°/s):", gyro_range)
        
        layout.addWidget(config_group)
        
        return tab
    
    def _add_file_reader_fields(self, layout):
        """Add FileReader configuration fields."""
        file_path = QLineEdit()
        file_path.setObjectName("file_reader_path")
        
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(30)
        browse_btn.setObjectName("file_reader_browse")
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(file_path)
        path_layout.addWidget(browse_btn)
        
        layout.addRow("File Path:", path_layout)
        
        chunk_size = QSpinBox()
        chunk_size.setObjectName("file_reader_chunk_size")
        chunk_size.setRange(512, 65536)
        chunk_size.setValue(4096)
        chunk_size.setSingleStep(512)
        layout.addRow("Chunk Size:", chunk_size)
    
    def _add_serial_reader_fields(self, layout):
        """Add SerialReader configuration fields."""
        port = QLineEdit()
        port.setObjectName("serial_reader_port")
        layout.addRow("Port:", port)
        
        baudrate = QComboBox()
        baudrate.setObjectName("serial_reader_baudrate")
        baudrate.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        baudrate.setCurrentText("115200")
        layout.addRow("Baudrate:", baudrate)
        
        timeout = QDoubleSpinBox()
        timeout.setObjectName("serial_reader_timeout")
        timeout.setRange(0.1, 10.0)
        timeout.setValue(1.0)
        timeout.setSingleStep(0.1)
        layout.addRow("Timeout (s):", timeout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Apply and reset buttons
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        
        # Tab widget
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def set_config(self, config):
        """Set the current configuration."""
        self.current_config = config
        self._update_ui_from_config()
    
    def _update_ui_from_config(self):
        """Update UI elements from the current configuration."""
        # TODO: Implement logic to update UI based on configuration
        pass
    
    def _get_config_from_ui(self):
        """Get configuration from UI elements."""
        # TODO: Implement logic to get configuration from UI
        config = {}
        return config
    
    @pyqtSlot()
    def _on_apply_clicked(self):
        """Handle apply button click."""
        # Get configuration from UI
        config = self._get_config_from_ui()
        
        # Emit signal
        self.config_changed.emit(config)
    
    @pyqtSlot()
    def _on_reset_clicked(self):
        """Handle reset button click."""
        # Reset UI to current configuration
        self._update_ui_from_config()
    
    @pyqtSlot(int)
    def _on_tab_changed(self, index):
        """Handle tab change."""
        # TODO: Implement tab change logic if needed
        pass