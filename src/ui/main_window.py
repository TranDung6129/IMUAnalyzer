from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QTabWidget, 
                             QVBoxLayout, QHBoxLayout, QWidget, 
                             QStatusBar, QToolBar, QMenuBar, QMenu, 
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings
from PyQt6.QtGui import QAction, QIcon

from src.ui.connection_panel import ConnectionPanel
from src.ui.config_panel import ConfigPanel
from src.ui.visualizers.dashboard import Dashboard
from src.ui.controls.pipeline_controls import PipelineControls
from src.ui_adapter.engine_adapter import EngineAdapter

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, engine_adapter=None):
        """Initialize the main window."""
        super().__init__()
        
        # Store references
        self.engine_adapter = engine_adapter or EngineAdapter()
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals/slots
        self._connect_signals()
        
        # Load settings
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Window properties
        self.setWindowTitle("IMU Analyzer")
        self.setMinimumSize(1024, 768)
        
        # Create central widget with dashboard
        from src.ui.visualizers.dashboard.grid_dashboard_panel import GridDashboardPanel
        from src.ui.visualizers.dashboard.dashboard_control_panel import DashboardControlPanel

        # Tạo widget container với layout dọc
        self.dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout(self.dashboard_container)
        dashboard_layout.setContentsMargins(1, 1, 1, 1)

        # Tạo và thêm GridDashboardPanel
        self.grid_dashboard = GridDashboardPanel()
        dashboard_layout.addWidget(self.grid_dashboard)

        # Tạo và thêm DashboardControlPanel
        self.dashboard_control = DashboardControlPanel(self.grid_dashboard)
        dashboard_layout.addWidget(self.dashboard_control)

        # Đặt container làm central widget
        self.setCentralWidget(self.dashboard_container)
        
        # Create dockable panels
        self._create_docks()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create toolbar
        self._create_toolbar()
        
        # Create menu
        self._create_menu()
    
    def _create_docks(self):
        """Create dockable panels."""
        # Connection panel dock
        self.connection_dock = QDockWidget("Connection", self)
        self.connection_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                            Qt.DockWidgetArea.RightDockWidgetArea)
        self.connection_panel = ConnectionPanel()
        self.connection_dock.setWidget(self.connection_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.connection_dock)
        
        # Configuration panel dock
        self.config_dock = QDockWidget("Configuration", self)
        self.config_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                        Qt.DockWidgetArea.RightDockWidgetArea)
        self.config_panel = ConfigPanel()
        self.config_dock.setWidget(self.config_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.config_dock)
    
    def _create_toolbar(self):
        """Create the main toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        
        # Add pipeline controls to toolbar
        self.pipeline_controls = PipelineControls()
        self.toolbar.addWidget(self.pipeline_controls)
    
    def _create_menu(self):
        """Create the application menu."""
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)
        
        # File actions
        open_action = QAction("&Open Configuration...", self)
        open_action.triggered.connect(self._on_open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Configuration...", self)
        save_action.triggered.connect(self._on_save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        self.menu_bar.addMenu(view_menu)
        
        view_menu.addAction(self.connection_dock.toggleViewAction())
        view_menu.addAction(self.config_dock.toggleViewAction())
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect pipeline controls to engine adapter
        self.pipeline_controls.start_clicked.connect(self._on_start_pipeline)
        self.pipeline_controls.stop_clicked.connect(self._on_stop_pipeline)
        
        # Connect connection panel
        self.connection_panel.connection_changed.connect(self._on_connection_changed)
    
    def _load_settings(self):
        """Load application settings."""
        settings = QSettings("IMUAnalyzer", "IMUAnalyzer")
        
        # Load window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load window state (dock positions, etc)
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings
        settings = QSettings("IMUAnalyzer", "IMUAnalyzer")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Accept the close event
        event.accept()
    
    @pyqtSlot()
    def _on_open_config(self):
        """Handle opening configuration file."""
        # TODO: Implement open configuration
        self.status_bar.showMessage("Open configuration not implemented")
    
    @pyqtSlot()
    def _on_save_config(self):
        """Handle saving configuration file."""
        # TODO: Implement save configuration
        self.status_bar.showMessage("Save configuration not implemented")
    
    @pyqtSlot()
    def _on_start_pipeline(self):
        """Handle starting the pipeline."""
        config_path = self.config_panel.get_selected_config()
        if config_path:
            self.engine_adapter.start_pipeline(config_path)
            self.status_bar.showMessage(f"Started pipeline with config: {config_path}")
        else:
            self.status_bar.showMessage("No configuration selected")
    
    @pyqtSlot()
    def _on_stop_pipeline(self):
        """Handle stopping the pipeline."""
        self.engine_adapter.stop_pipeline()
        self.status_bar.showMessage("Pipeline stopped")
    
    @pyqtSlot(dict)
    def _on_connection_changed(self, connection_info):
        """Handle connection changes."""
        self.status_bar.showMessage(f"Connection changed: {connection_info}")