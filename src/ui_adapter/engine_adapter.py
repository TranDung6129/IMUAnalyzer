import threading
import time
from typing import List, Dict, Any, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

class EngineAdapter(QObject):
    """Adapter between UI and core engine."""
    
    # Custom signals
    engine_started = pyqtSignal()
    engine_stopped = pyqtSignal()
    engine_error = pyqtSignal(str)
    
    data_received = pyqtSignal(dict)  # Emitted when new data is available
    
    def __init__(self, parent=None):
        """Initialize the engine adapter."""
        super().__init__(parent)
        
        # Engine reference (will be set later)
        self.engine = None
        
        # Engine thread
        self.engine_thread = None
        
        # Running status
        self.running = False
    
    def set_engine(self, engine):
        """Set the engine reference."""
        self.engine = engine
    
    def start_pipeline(self, config_path):
        """
        Start the pipeline with the given configuration.
        
        Args:
            config_path: Path to configuration file
        """
        if not self.engine:
            self.engine_error.emit("Engine not initialized")
            return
        
        if self.running:
            self.engine_error.emit("Engine already running")
            return
        
        # Start engine in a separate thread
        self.engine_thread = threading.Thread(
            target=self._run_engine,
            args=(config_path,)
        )
        self.engine_thread.daemon = True
        self.engine_thread.start()
        
        # Update status
        self.running = True
        self.engine_started.emit()
    
    def stop_pipeline(self):
        """Stop the pipeline."""
        if not self.running:
            return
        
        try:
            # Stop the engine
            if self.engine:
                self.engine.stop()
            
            # Wait for thread to finish
            if self.engine_thread and self.engine_thread.is_alive():
                self.engine_thread.join(timeout=3.0)
        except Exception as e:
            self.engine_error.emit(f"Error stopping engine: {str(e)}")
        finally:
            # Update status
            self.running = False
            self.engine_stopped.emit()

    def _run_engine(self, config_path):
        """
        Run the engine in a separate thread.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            # Setup the engine
            self.engine.setup(config_path)
            
            # Register data callback
            self._register_data_callback()
            
            # Run the engine
            self.engine.run()
        except Exception as e:
            # Emit error signal
            self.engine_error.emit(f"Error running engine: {str(e)}")
        finally:
            # Update status
            self.running = False
            self.engine_stopped.emit()
    
    def _register_data_callback(self):
        """Register callback to receive data from the engine."""
        if not self.engine:
            return
        
        # Find all visualizers in the pipeline
        for pipeline in self.engine.pipelines:
            for visualizer in pipeline.visualizers:
                # Monkey patch the visualize method to capture data
                original_visualize = visualizer.visualize
                
                def visualize_wrapper(data, original_method=original_visualize):
                    # Call original method
                    original_method(data)
                    
                    # Emit signal with data
                    self.data_received.emit({
                        "type": "visualize",
                        "data": data
                    })
                
                visualizer.visualize = visualize_wrapper