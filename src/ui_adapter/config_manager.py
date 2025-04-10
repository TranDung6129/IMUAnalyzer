import os
import json
import yaml
from typing import Dict, List, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings

class ConfigManager(QObject):
    """Manager for UI configuration."""
    
    # Custom signals
    config_loaded = pyqtSignal(dict)
    config_saved = pyqtSignal(str)
    config_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the config manager."""
        super().__init__(parent)
        
        # Default config directory
        self.config_dir = os.path.join(os.getcwd(), "config")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Current configuration
        self.current_config = {}
        self.current_config_path = None
    
    def load_config(self, config_path):
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration or None if error
        """
        try:
            # Check file extension
            if config_path.endswith((".yaml", ".yml")):
                # Load YAML config
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
            elif config_path.endswith(".json"):
                # Load JSON config
                with open(config_path, "r") as f:
                    config = json.load(f)
            else:
                self.config_error.emit(f"Unsupported file format: {os.path.basename(config_path)}")
                return None
            
            # Store current config
            self.current_config = config
            self.current_config_path = config_path
            
            # Emit signal
            self.config_loaded.emit(config)
            
            return config
        except Exception as e:
            self.config_error.emit(f"Error loading config: {str(e)}")
            return None
    
    def save_config(self, config, config_path=None):
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            config_path: Path to save configuration to (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        # Use current path if not specified
        if config_path is None:
            config_path = self.current_config_path
        
        if not config_path:
            self.config_error.emit("No config path specified")
            return False
        
        try:
            # Check file extension
            if config_path.endswith((".yaml", ".yml")):
                # Save as YAML
                with open(config_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
            elif config_path.endswith(".json"):
                # Save as JSON
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
            else:
                # Default to YAML
                if not config_path.endswith((".yaml", ".yml")):
                    config_path += ".yaml"
                
                with open(config_path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
            
            # Store current config
            self.current_config = config
            self.current_config_path = config_path
            
            # Emit signal
            self.config_saved.emit(config_path)
            
            return True
        except Exception as e:
            self.config_error.emit(f"Error saving config: {str(e)}")
            return False
    
    def get_available_configs(self):
        """
        Get a list of available configuration files.
        
        Returns:
            List of configuration file paths
        """
        configs = []
        
        # Check if config directory exists
        if not os.path.exists(self.config_dir):
            return configs
        
        # Find all YAML and JSON files
        for file in os.listdir(self.config_dir):
            if file.endswith((".yaml", ".yml", ".json")):
                configs.append(os.path.join(self.config_dir, file))
        
        return configs
    
    def create_default_config(self, config_path=None):
        """
        Create a default configuration file.
        
        Args:
            config_path: Path to save configuration to (optional)
            
        Returns:
            Path to created configuration file or None if error
        """
        # Generate default config path if not specified
        if config_path is None:
            config_path = os.path.join(self.config_dir, "default_config.yaml")
        
        # Create default configuration
        default_config = {
            "pipeline": {
                "name": "Default Pipeline",
                "use_threading": True,
                "reader": {
                    "type": "SerialReader",
                    "config": {
                        "port": "/dev/ttyUSB0",
                        "baudrate": 115200
                    }
                },
                "decoder": {
                    "type": "WitMotionDecoder",
                    "config": {
                        "sensor_id": "imu1",
                        "acc_range": 16.0,
                        "gyro_range": 2000.0
                    }
                },
                "processors": [
                    {
                        "type": "LowPassFilterProcessor",
                        "config": {
                            "cutoff_freq": 10.0,
                            "sample_rate": 100.0
                        }
                    }
                ],
                "visualizers": [
                    {
                        "type": "TimeSeriesVisualizer",
                        "config": {
                            "channels": ["x", "y", "z"],
                            "title": "Acceleration"
                        }
                    }
                ]
            }
        }
        
        # Save config
        if self.save_config(default_config, config_path):
            return config_path
        
        return None
    
    def get_current_config(self):
        """
        Get the current configuration.
        
        Returns:
            Current configuration dictionary
        """
        return self.current_config
    
    def get_current_config_path(self):
        """
        Get the path to the current configuration file.
        
        Returns:
            Path to current configuration file or None if not set
        """
        return self.current_config_path