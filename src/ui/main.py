import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from src.ui.main_window import MainWindow
from src.ui.utils.themes import apply_theme
from src.ui_adapter.engine_adapter import EngineAdapter
from src.ui_adapter.data_bridge import DataBridge
from src.ui_adapter.config_manager import ConfigManager

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="IMU Analyzer")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--theme", help="UI theme to use", default="Light")
    return parser.parse_args()

def main():
    """Main entry point for the UI application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("IMU Analyzer")
    app.setOrganizationName("IMUAnalyzer")
    
    # Apply theme
    apply_theme(args.theme)
    
    # Create adapters
    engine_adapter = EngineAdapter()
    data_bridge = DataBridge()
    config_manager = ConfigManager()
    
    # Connect signals
    engine_adapter.data_received.connect(data_bridge.process_data)
    
    # Create main window
    main_window = MainWindow(engine_adapter)
    
    # Show main window
    main_window.show()
    
    # Load configuration if specified
    if args.config:
        config_path = args.config
        if os.path.exists(config_path):
            config = config_manager.load_config(config_path)
            if config:
                # TODO: Apply configuration to UI
                pass
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())