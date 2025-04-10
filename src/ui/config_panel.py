from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QComboBox, QPushButton, QLineEdit,
                             QGroupBox, QFileDialog, QTextEdit, QListWidget,
                             QStackedWidget, QTreeView)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSettings, QDir
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
import os
import yaml

class ConfigPanel(QWidget):
    """Panel for managing pipeline configurations."""
    
    # Custom signals
    config_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the configuration panel."""
        super().__init__(parent)
        
        # Setup internal variables
        self.config_dir = os.path.join(os.getcwd(), "config")
        self.current_config = None
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Load configurations
        self._refresh_configs()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Config selection group
        config_group = QGroupBox("Pipeline Configuration")
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)
        
        # Config list
        self.config_list = QListWidget()
        config_layout.addWidget(self.config_list)
        
        # Buttons for managing configs
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        button_layout.addWidget(self.refresh_button)
        
        self.new_button = QPushButton("New")
        button_layout.addWidget(self.new_button)
        
        self.edit_button = QPushButton("Edit")
        button_layout.addWidget(self.edit_button)
        
        config_layout.addLayout(button_layout)
        
        main_layout.addWidget(config_group)
        
        # Config editor group
        editor_group = QGroupBox("Configuration Editor")
        editor_layout = QVBoxLayout()
        editor_group.setLayout(editor_layout)
        
        # Config editor
        self.config_editor = QTextEdit()
        self.config_editor.setFont(QFont("Courier New", 10))
        editor_layout.addWidget(self.config_editor)
        
        # Editor buttons
        editor_buttons = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        editor_buttons.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        editor_buttons.addWidget(self.cancel_button)
        
        editor_layout.addLayout(editor_buttons)
        
        main_layout.addWidget(editor_group)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Config list
        self.config_list.currentItemChanged.connect(self._on_config_selected)
        
        # Buttons
        self.refresh_button.clicked.connect(self._refresh_configs)
        self.new_button.clicked.connect(self._on_new_config)
        self.edit_button.clicked.connect(self._on_edit_config)
        self.save_button.clicked.connect(self._on_save_config)
        self.cancel_button.clicked.connect(self._on_cancel_edit)
    
    def _refresh_configs(self):
        """Refresh the list of configurations."""
        # Remember selected config
        current_item = self.config_list.currentItem()
        current_config = current_item.text() if current_item else None
        
        # Clear the list
        self.config_list.clear()
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Get all yaml files in config directory
        for file in os.listdir(self.config_dir):
            if file.endswith(".yaml") or file.endswith(".yml"):
                self.config_list.addItem(file)
        
        # Try to restore previously selected config
        if current_config:
            items = self.config_list.findItems(current_config, Qt.MatchExactly)
            if items:
                self.config_list.setCurrentItem(items[0])
    
    def get_selected_config(self):
        """Get the full path of the selected configuration file."""
        item = self.config_list.currentItem()
        if item:
            return os.path.join(self.config_dir, item.text())
        return None
    
    @pyqtSlot()
    def _on_config_selected(self, current, previous):
        """Handle configuration selection."""
        if current:
            config_path = os.path.join(self.config_dir, current.text())
            self.current_config = config_path
            
            # Emit signal
            self.config_changed.emit(config_path)
            
            # Load config content
            try:
                with open(config_path, "r") as f:
                    content = f.read()
                self.config_editor.setPlainText(content)
            except Exception as e:
                self.config_editor.setPlainText(f"Error loading config: {e}")
    
    @pyqtSlot()
    def _on_new_config(self):
        """Handle new configuration button click."""
        # Show file dialog to get new config name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "New Configuration File",
            self.config_dir,
            "YAML Files (*.yaml *.yml)"
        )
        
        if file_path:
            # Ensure it has .yaml extension
            if not file_path.endswith(".yaml") and not file_path.endswith(".yml"):
                file_path += ".yaml"
            
            # Create empty config with template
            template = """
# IMU Analyzer Pipeline Configuration

pipeline:
  name: "New Pipeline"
  use_threading: true
  
  reader:
    type: "SerialReader"
    config:
      port: "/dev/ttyUSB0"
      baudrate: 115200
  
  decoder:
    type: "WitMotionDecoder"
    config:
      sensor_id: "imu1"
      acc_range: 16.0
      gyro_range: 2000.0
  
  processors:
    - type: "LowPassFilterProcessor"
      config:
        cutoff_freq: 10.0
        sample_rate: 100.0
  
  visualizers:
    - type: "TimeSeriesVisualizer"
      config:
        channels: ["x", "y", "z"]
        title: "Acceleration"
"""
            try:
                with open(file_path, "w") as f:
                    f.write(template.strip())
                
                # Refresh config list
                self._refresh_configs()
                
                # Select the new config
                file_name = os.path.basename(file_path)
                items = self.config_list.findItems(file_name, Qt.MatchExactly)
                if items:
                    self.config_list.setCurrentItem(items[0])
            except Exception as e:
                # TODO: Show error message
                print(f"Error creating config: {e}")
    
    @pyqtSlot()
    def _on_edit_config(self):
        """Handle edit configuration button click."""
        # Current item is already loaded in the editor
        pass
    
    @pyqtSlot()
    def _on_save_config(self):
        """Handle save configuration button click."""
        if not self.current_config:
            return
        
        # Get editor content
        content = self.config_editor.toPlainText()
        
        # Validate YAML
        try:
            yaml.safe_load(content)
        except Exception as e:
            # TODO: Show error message
            print(f"Invalid YAML: {e}")
            return
        
        # Save to file
        try:
            with open(self.current_config, "w") as f:
                f.write(content)
        except Exception as e:
            # TODO: Show error message
            print(f"Error saving config: {e}")
    
    @pyqtSlot()
    def _on_cancel_edit(self):
        """Handle cancel edit button click."""
        # Reload current config
        if self.current_config:
            try:
                with open(self.current_config, "r") as f:
                    content = f.read()
                self.config_editor.setPlainText(content)
            except Exception as e:
                self.config_editor.setPlainText(f"Error loading config: {e}")