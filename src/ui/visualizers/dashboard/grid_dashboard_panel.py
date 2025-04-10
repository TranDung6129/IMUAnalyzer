"""
Grid Dashboard Panel for displaying multiple visualizers in a grid layout.
"""
import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize

try:
    # Thử import PyQtGraph's DockArea
    from pyqtgraph.dockarea import DockArea, Dock
    USE_PYQTGRAPH_DOCK = True
except ImportError:
    # Fallback to QGridLayout
    USE_PYQTGRAPH_DOCK = False

from src.ui.visualizers.dashboard.draggable_visualizer_widget import DraggableVisualizerWidget

class GridDashboardPanel(QWidget):
    """Panel that displays multiple visualizers in a grid layout."""
    
    # Tín hiệu khi widget được thêm vào hoặc xóa đi
    widget_added = pyqtSignal(str, object)  # widget_id, widget
    widget_removed = pyqtSignal(str)  # widget_id
    
    def __init__(self, parent=None):
        """Initialize the grid dashboard panel."""
        super().__init__(parent)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tạo dock area hoặc grid layout tùy thuộc vào dependencies có sẵn
        if USE_PYQTGRAPH_DOCK:
            self.dock_area = DockArea()
            self.main_layout.addWidget(self.dock_area)
            self.widgets = {}  # dict to store widgets by ID
        else:
            self.grid_widget = QWidget()
            self.grid_layout = QGridLayout(self.grid_widget)
            self.grid_layout.setSpacing(4)
            self.main_layout.addWidget(self.grid_widget)
            self.widgets = {}
            self.current_row = 0
            self.current_col = 0
            self.max_cols = 2  # Default columns
    
    def add_widget(self, content_widget, title, widget_id=None):
        """
        Add a new widget to the dashboard.
        
        Args:
            content_widget: The actual visualizer widget to add
            title: Title for the widget
            widget_id: Unique ID for the widget (will be generated if None)
            
        Returns:
            The ID of the added widget
        """
        # Generate ID if not provided
        if widget_id is None:
            widget_id = f"widget_{len(self.widgets) + 1}"
        
        # Create draggable container if not using PyQtGraph DockArea
        if USE_PYQTGRAPH_DOCK:
            # Using PyQtGraph DockArea
            dock = Dock(title, size=(300, 200))
            dock.addWidget(content_widget)
            
            # Add to dock area
            if self.widgets:
                # Add relative to last added widget
                last_dock = list(self.widgets.values())[-1]
                self.dock_area.addDock(dock, 'right', last_dock)
            else:
                # First widget
                self.dock_area.addDock(dock)
            
            # Store reference
            self.widgets[widget_id] = dock
            
            # Emit signal
            self.widget_added.emit(widget_id, content_widget)
            
            return widget_id
        else:
            # Using QGridLayout
            
            # Create draggable container
            container = DraggableVisualizerWidget(content_widget, title, widget_id)
            
            # Connect signals
            container.close_requested.connect(lambda: self.remove_widget(widget_id))
            
            # Add to grid
            self.grid_layout.addWidget(container, self.current_row, self.current_col)
            
            # Update grid positions
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1
            
            # Store reference
            self.widgets[widget_id] = container
            
            # Emit signal
            self.widget_added.emit(widget_id, content_widget)
            
            return widget_id
    
    def remove_widget(self, widget_id):
        """
        Remove a widget from the dashboard.
        
        Args:
            widget_id: ID of the widget to remove
        """
        if widget_id not in self.widgets:
            return
        
        if USE_PYQTGRAPH_DOCK:
            # Remove from DockArea
            dock = self.widgets[widget_id]
            dock.close()
        else:
            # Remove from QGridLayout
            container = self.widgets[widget_id]
            self.grid_layout.removeWidget(container)
            container.deleteLater()
        
        # Remove from dictionary
        del self.widgets[widget_id]
        
        # Emit signal
        self.widget_removed.emit(widget_id)
        
        # If using QGridLayout, we need to rearrange widgets
        if not USE_PYQTGRAPH_DOCK:
            self._rearrange_widgets()
    
    def _rearrange_widgets(self):
        """Rearrange widgets in grid layout after removal."""
        if USE_PYQTGRAPH_DOCK:
            return  # Not needed for DockArea
        
        # Store widgets
        widgets = list(self.widgets.values())
        
        # Clear grid
        for widget in widgets:
            self.grid_layout.removeWidget(widget)
        
        # Re-add widgets
        row = 0
        col = 0
        for widget in widgets:
            self.grid_layout.addWidget(widget, row, col)
            col += 1
            if col >= self.max_cols:
                col = 0
                row += 1
        
        # Update current position
        self.current_row = row
        self.current_col = col
    
    def clear_all(self):
        """Remove all widgets from the dashboard."""
        # Make a copy of keys to avoid modifying dict during iteration
        widget_ids = list(self.widgets.keys())
        
        for widget_id in widget_ids:
            self.remove_widget(widget_id)
    
    def get_widget(self, widget_id):
        """
        Get the widget with the specified ID.
        
        Args:
            widget_id: ID of the widget to get
            
        Returns:
            The widget or None if not found
        """
        if widget_id not in self.widgets:
            return None
        
        if USE_PYQTGRAPH_DOCK:
            # For DockArea, we need to get the actual widget from the dock
            return self.widgets[widget_id].widgets[0]
        else:
            # For QGridLayout, we need to get the content_widget from the container
            return self.widgets[widget_id].content_widget
    
    def get_layout_state(self):
        """
        Get the current layout state.
        
        Returns:
            Dictionary representing the current layout state
        """
        if USE_PYQTGRAPH_DOCK:
            # PyQtGraph DockArea has built-in state saving
            return self.dock_area.saveState()
        else:
            # For QGridLayout, we need to manually save widget positions
            state = {}
            
            for widget_id, container in self.widgets.items():
                # Find position in grid
                index = self.grid_layout.indexOf(container)
                if index >= 0:
                    row, col, _, _ = self.grid_layout.getItemPosition(index)
                    
                    # Save position
                    state[widget_id] = {
                        'row': row,
                        'col': col,
                        'title': container.title_label.text()
                    }
            
            return state
    
    def restore_layout_state(self, state):
        """
        Restore the layout state.
        
        Args:
            state: Dictionary representing layout state
            
        Returns:
            True if successful, False otherwise
        """
        if USE_PYQTGRAPH_DOCK:
            # PyQtGraph DockArea has built-in state restoration
            try:
                self.dock_area.restoreState(state)
                return True
            except Exception as e:
                print(f"Error restoring dock layout: {e}")
                return False
        else:
            # For QGridLayout, we need to manually restore widget positions
            try:
                for widget_id, info in state.items():
                    if widget_id in self.widgets:
                        container = self.widgets[widget_id]
                        
                        # Remove from current position
                        self.grid_layout.removeWidget(container)
                        
                        # Add to saved position
                        self.grid_layout.addWidget(container, info['row'], info['col'])
                        
                        # Update title if needed
                        if 'title' in info:
                            container.title_label.setText(info['title'])
                
                return True
            except Exception as e:
                print(f"Error restoring grid layout: {e}")
                return False