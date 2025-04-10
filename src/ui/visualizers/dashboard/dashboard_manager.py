"""
Manager for dashboard configurations and layouts.
"""
import os
import json
from PyQt6.QtCore import QObject, pyqtSignal

class DashboardManager(QObject):
    """Manager for dashboard configurations and layouts."""
    
    # Tín hiệu
    layout_loaded = pyqtSignal(dict)
    layout_saved = pyqtSignal(str)
    
    def __init__(self, dashboard_panel, parent=None):
        """Initialize dashboard manager."""
        super().__init__(parent)
        
        self.dashboard_panel = dashboard_panel
        self.widget_configs = {}  # Configuration for each widget
    
    def save_layout(self, file_path):
        """
        Save dashboard layout to file.
        
        Args:
            file_path: Path to save the layout file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get layout state from panel
            layout_state = self.dashboard_panel.get_layout_state()
            
            # Add widget configurations
            layout_data = {
                'layout_state': layout_state,
                'widget_configs': self.widget_configs
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(layout_data, f, indent=2)
            
            # Emit signal
            self.layout_saved.emit(file_path)
            
            return True
        except Exception as e:
            print(f"Error saving layout: {e}")
            return False
    
    def load_layout(self, file_path):
        """
        Load dashboard layout from file.
        
        Args:
            file_path: Path to layout file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r') as f:
                layout_data = json.load(f)
            
            # Clear current layout
            self.dashboard_panel.clear_all()
            
            # TODO: Recreate widgets based on saved configuration
            # For now, we'll just restore the layout state if we have matching widgets
            
            # Restore layout state
            if 'layout_state' in layout_data:
                self.dashboard_panel.restore_layout_state(layout_data['layout_state'])
            
            # Load widget configurations
            if 'widget_configs' in layout_data:
                self.widget_configs = layout_data['widget_configs']
            
            # Emit signal
            self.layout_loaded.emit(layout_data)
            
            return True
        except Exception as e:
            print(f"Error loading layout: {e}")
            return False
    
    def register_widget_config(self, widget_id, config):
        """
        Register configuration for a widget.
        
        Args:
            widget_id: ID of the widget
            config: Configuration dictionary
        """
        self.widget_configs[widget_id] = config
    
    def get_widget_config(self, widget_id):
        """
        Get configuration for a widget.
        
        Args:
            widget_id: ID of the widget
            
        Returns:
            Configuration dictionary or None if not found
        """
        return self.widget_configs.get(widget_id)