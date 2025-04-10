from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QComboBox, QPushButton, QLineEdit,
                             QGroupBox, QFileDialog, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSettings
import serial.tools.list_ports

class ConnectionPanel(QWidget):
    """Panel for managing connections to sensors and data sources."""
    
    # Custom signals
    connection_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize the connection panel."""
        super().__init__(parent)
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Load saved settings
        self._load_settings()
        
        # Initially refresh serial ports
        self._refresh_serial_ports()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Serial connection group
        serial_group = QGroupBox("Serial Connection")
        serial_layout = QGridLayout()
        serial_group.setLayout(serial_layout)
        
        # Port selection
        serial_layout.addWidget(QLabel("Port:"), 0, 0)
        self.port_combo = QComboBox()
        serial_layout.addWidget(self.port_combo, 0, 1)
        
        self.refresh_button = QPushButton("Refresh")
        serial_layout.addWidget(self.refresh_button, 0, 2)
        
        # Baudrate
        serial_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baudrate_combo.setCurrentText("115200")
        serial_layout.addWidget(self.baudrate_combo, 1, 1, 1, 2)
        
        # Connect button
        self.connect_button = QPushButton("Connect")
        serial_layout.addWidget(self.connect_button, 2, 0, 1, 3)
        
        main_layout.addWidget(serial_group)
        
        # File connection group
        file_group = QGroupBox("File Connection")
        file_layout = QGridLayout()
        file_group.setLayout(file_layout)
        
        # File path
        file_layout.addWidget(QLabel("File:"), 0, 0)
        self.file_path = QLineEdit()
        file_layout.addWidget(self.file_path, 0, 1)
        
        self.browse_button = QPushButton("Browse")
        file_layout.addWidget(self.browse_button, 0, 2)
        
        # Load button
        self.load_button = QPushButton("Load File")
        file_layout.addWidget(self.load_button, 1, 0, 1, 3)
        
        main_layout.addWidget(file_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Serial connection
        self.refresh_button.clicked.connect(self._refresh_serial_ports)
        self.connect_button.clicked.connect(self._on_serial_connect)
        
        # File connection
        self.browse_button.clicked.connect(self._on_browse_file)
        self.load_button.clicked.connect(self._on_load_file)
    
    def _load_settings(self):
        """Load saved connection settings."""
        settings = QSettings("IMUAnalyzer", "IMUAnalyzer")
        
        # Load baudrate
        baudrate = settings.value("connection/baudrate")
        if baudrate:
            index = self.baudrate_combo.findText(baudrate)
            if index >= 0:
                self.baudrate_combo.setCurrentIndex(index)
        
        # Load file path
        file_path = settings.value("connection/file_path")
        if file_path:
            self.file_path.setText(file_path)
    
    def _save_settings(self):
        """Save connection settings."""
        settings = QSettings("IMUAnalyzer", "IMUAnalyzer")
        
        # Save baudrate
        settings.setValue("connection/baudrate", self.baudrate_combo.currentText())
        
        # Save file path
        settings.setValue("connection/file_path", self.file_path.text())
    
    def _refresh_serial_ports(self):
        """Refresh the list of available serial ports."""
        # Remember selected port
        current_port = self.port_combo.currentText()
        
        # Clear the combobox
        self.port_combo.clear()
        
        # Get all serial ports
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        
        # Add ports to combo box
        self.port_combo.addItems(ports)
        
        # Try to restore previously selected port
        if current_port:
            index = self.port_combo.findText(current_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
    
    @pyqtSlot()
    def _on_serial_connect(self):
        """Handle serial connection button click."""
        if self.connect_button.text() == "Connect":
            # Get connection parameters
            port = self.port_combo.currentText()
            baudrate = int(self.baudrate_combo.currentText())
            
            if not port:
                # TODO: Show error message
                return
            
            # Emit connection info
            connection_info = {
                "type": "serial",
                "port": port,
                "baudrate": baudrate
            }
            self.connection_changed.emit(connection_info)
            
            # Update button
            self.connect_button.setText("Disconnect")
            
            # Save settings
            self._save_settings()
        else:
            # Emit disconnection info
            connection_info = {
                "type": "disconnect"
            }
            self.connection_changed.emit(connection_info)
            
            # Update button
            self.connect_button.setText("Connect")
    
    @pyqtSlot()
    def _on_browse_file(self):
        """Handle file browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "All Files (*);;Binary Files (*.bin);;CSV Files (*.csv)"
        )
        
        if file_path:
            self.file_path.setText(file_path)
    
    @pyqtSlot()
    def _on_load_file(self):
        """Handle file load button click."""
        file_path = self.file_path.text()
        
        if not file_path:
            # TODO: Show error message
            return
        
        # Emit connection info
        connection_info = {
            "type": "file",
            "path": file_path
        }
        self.connection_changed.emit(connection_info)
        
        # Save settings
        self._save_settings()