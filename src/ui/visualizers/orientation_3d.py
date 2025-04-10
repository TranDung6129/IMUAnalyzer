from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QCheckBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from math import sin, cos, radians

class Orientation3D(QWidget):
    """Widget for 3D visualization of IMU orientation."""
    
    def __init__(self, parent=None):
        """Initialize the 3D orientation visualization widget."""
        super().__init__(parent)
        
        # Current orientation (euler angles in degrees)
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        # Setup UI
        self._setup_ui()
        
        # Create 3D model
        self._create_model()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # OpenGL view widget
        self.view = gl.GLViewWidget()
        
        # Set camera position
        self.view.setCameraPosition(distance=7, elevation=20, azimuth=45)
        
        # Add coordinate axes
        self._add_axes()
        
        # Add to layout
        main_layout.addWidget(self.view)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # View preset selector
        controls_layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Perspective", "Top", "Side", "Front"])
        self.view_combo.currentTextChanged.connect(self._on_view_changed)
        controls_layout.addWidget(self.view_combo)
        
        # Show axes checkbox
        self.axes_cb = QCheckBox("Show Axes")
        self.axes_cb.setChecked(True)
        self.axes_cb.toggled.connect(self._on_show_axes_toggled)
        controls_layout.addWidget(self.axes_cb)
        
        # Add stretch to push controls to the left
        controls_layout.addStretch(1)
        
        # Add controls to main layout
        main_layout.addLayout(controls_layout)
    
    def _add_axes(self):
        """Add coordinate axes to the view."""
        # X-axis (Red)
        x_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [1, 0, 0]]),
            color=(1, 0, 0, 1),
            width=2.0,
            antialias=True
        )
        self.view.addItem(x_axis)
        
        # Y-axis (Green)
        y_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 1, 0]]),
            color=(0, 1, 0, 1),
            width=2.0,
            antialias=True
        )
        self.view.addItem(y_axis)
        
        # Z-axis (Blue)
        z_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 0, 1]]),
            color=(0, 0, 1, 1),
            width=2.0,
            antialias=True
        )
        self.view.addItem(z_axis)
        
        # Save references
        self.axes = [x_axis, y_axis, z_axis]
    
    def _create_model(self):
        """Create the 3D model of the IMU sensor."""
        # Create a cuboid mesh to represent the IMU
        self.imu_model = gl.GLMeshItem(
            meshdata=self._create_cuboid(1.5, 1.0, 0.2),
            smooth=False,
            color=(0.8, 0.8, 0.8, 0.8),
            shader="shaded",
            glOptions="translucent"
        )
        self.view.addItem(self.imu_model)
        
        # Add direction indicator (arrow)
        self.arrow = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [1.5, 0, 0]]),
            color=(1, 0.5, 0, 1),
            width=4.0,
            antialias=True
        )
        self.view.addItem(self.arrow)
    
    def _create_cuboid(self, width, height, depth):
        """Create a cuboid mesh with the given dimensions."""
        # Define vertices
        w, h, d = width/2, height/2, depth/2
        verts = np.array([
            [ w,  h,  d], [-w,  h,  d], [-w, -h,  d], [ w, -h,  d],
            [ w,  h, -d], [-w,  h, -d], [-w, -h, -d], [ w, -h, -d]
        ])
        
        # Define faces by connecting vertices
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Top face
            [4, 7, 6], [4, 6, 5],  # Bottom face
            [0, 4, 5], [0, 5, 1],  # Front face
            [1, 5, 6], [1, 6, 2],  # Right face
            [2, 6, 7], [2, 7, 3],  # Back face
            [3, 7, 4], [3, 4, 0]   # Left face
        ])
        
        # Create mesh data
        mesh_data = gl.MeshData(vertexes=verts, faces=faces)
        return mesh_data
    
    def update_orientation(self, roll, pitch, yaw):
        """Update the 3D model orientation with Euler angles (in degrees)."""
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        
        # Convert Euler angles to rotation matrix
        rotation_matrix = self._euler_to_rotation_matrix(roll, pitch, yaw)
        
        # Apply rotation to the model
        self.imu_model.setTransform(rotation_matrix)
        
        # Update arrow direction
        start_point = np.array([0, 0, 0])
        end_point = np.dot(rotation_matrix[:3, :3], np.array([1.5, 0, 0]))
        self.arrow.setData(pos=np.array([start_point, end_point]))
    
    def _euler_to_rotation_matrix(self, roll, pitch, yaw):
        """Convert Euler angles to a 4x4 rotation matrix."""
        # Convert degrees to radians
        roll_rad = radians(roll)
        pitch_rad = radians(pitch)
        yaw_rad = radians(yaw)
        
        # Roll (X-axis rotation)
        cr, sr = cos(roll_rad), sin(roll_rad)
        rx = np.array([
            [1, 0, 0, 0],
            [0, cr, -sr, 0],
            [0, sr, cr, 0],
            [0, 0, 0, 1]
        ])
        
        # Pitch (Y-axis rotation)
        cp, sp = cos(pitch_rad), sin(pitch_rad)
        ry = np.array([
            [cp, 0, sp, 0],
            [0, 1, 0, 0],
            [-sp, 0, cp, 0],
            [0, 0, 0, 1]
        ])
        
        # Yaw (Z-axis rotation)
        cy, sy = cos(yaw_rad), sin(yaw_rad)
        rz = np.array([
            [cy, -sy, 0, 0],
            [sy, cy, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Combine rotations: R = Rz * Ry * Rx
        rotation_matrix = np.dot(np.dot(rz, ry), rx)
        return rotation_matrix
    
    @pyqtSlot(str)
    def _on_view_changed(self, text):
        """Handle view preset change."""
        if text == "Top":
            self.view.setCameraPosition(distance=7, elevation=90, azimuth=0)
        elif text == "Side":
            self.view.setCameraPosition(distance=7, elevation=0, azimuth=90)
        elif text == "Front":
            self.view.setCameraPosition(distance=7, elevation=0, azimuth=0)
        else:  # Perspective
            self.view.setCameraPosition(distance=7, elevation=20, azimuth=45)
    
    @pyqtSlot(bool)
    def _on_show_axes_toggled(self, checked):
        """Handle show axes checkbox toggle."""
        for axis in self.axes:
            axis.setVisible(checked)