"""
Utilities for serial port communication with IMU sensors.

This module provides functions for working with serial ports, 
including discovery, connection, and configuration.
"""

import sys
import time
import serial
import serial.tools.list_ports
from typing import List, Dict, Any, Optional, Tuple

class SerialConnectionError(Exception):
    """Exception raised for errors in the serial connection."""
    pass

def list_serial_ports() -> List[Dict[str, Any]]:
    """
    List all available serial ports on the system.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing port information.
    
    Eg:
        [
            {
                'device': '/dev/ttyUSB0',
                'name': 'USB Serial Device',
                'description': 'USB Serial Port',
                'hwid': 'USB VID:PID=1234:5678',
                'vid': 1234,
                'pid': 5678,
                'serial_number': 'ABC12345678'
            },
            # More ports...
        ]
    """
    ports = []

    for port in serial.tools.list_ports.comports(): # List all serial ports
        ports.append({
            'device': port.device,                  # Port name (e.g., COM3, /dev/ttyUSB0)
            'name': port.name,                      # Human-readable name of the port
            'description': port.description,        # Description of the port (e.g., USB Serial Device)
            'hwid': port.hwid,                      # Hardware ID (e.g., USB VID:PID=1234:5678)
            'vid': port.vid,                        # Vendor ID (e.g., 1234)
            'pid': port.pid,                        # Product ID (e.g., 5678)
        })
    
    return ports

def find_imu_ports(ports, vid=None, pid=None) -> List[Dict[str, Any]]:
    """
    Find serial ports that might be connected to IMU sensors.

    Args:
        :param ports: List of serial ports to filter.
        :param vid: Vendor ID to filter by (optional).
        :param pid: Product ID to filter by (optional).

    Returns:
        A list of port dictionaries that match the specified VID and PID.
    """
    imu_ports = []
    for port in ports:
        if (vid is None or port['vid'] == vid) and (pid is None or port['pid'] == pid):
            imu_ports.append(port)
    return imu_ports

def open_serial_connection(port: str, baudrate: int = 115200, timeout: float = 1.0, retry_count: int = 3) -> serial.Serial:
    """
    Create and open a serial connection to an IMU device.

    Args:
        port: Serial port name (e.g., 'COM3', '/dev/ttyUSB0').
        baudrate: Communication speed 
        timeout: Read timeout in seconds
        retry_count: Number of retries to open the connection.
    
    Returns:
        An open serial.Serial connection

    Raises:
        SerialConnectionError: If the serial connection cannot be established. (fails after retry)
    """

    attemp = 0
    last_error = None

    while attemp < retry_count:
        try:
            # Create and open serial connection
            ser = serial.Serial(
                port = port,
                baudrate = baudrate,
                timeout = timeout,
            )
        
            # Make sure it is open
            if not ser.is_open:
                ser.open()

            # Pause to allow the device to initialize
            time.sleep(0.1)

            return ser
    
        except serial.SerialException as e:
            last_error = e
            attemp += 1
            time.sleep(0.5)  # Wait before retrying

    # If reach here, all attempts failed
    raise SerialConnectionError(f"Failed to open serial port {port} after {retry_count} attemps: {last_error}")

def close_serial_connection(serial_conn: serial.Serial) -> None:
    """
    Safely close the serial connection.

    Args:
        serial_conn: The serial connection to close.
    
    Raises:
        SerialConnectionError: If the connection cannot be closed.
    """

    if serial_conn is None:
        return
    
    try:
        if serial_conn.is_open:
            # Flush buffers to ensure all data is sent/received
            serial_conn.flush()

            # Close the serial connection
            serial_conn.close()

    except serial.SerialException as e:
        raise SerialConnectionError(f"Failed to close serial connection: {e}")
            
def is_port_available(port: str) -> bool:
    """
    Check if a port is available for connection.

    Args: 
        port: Serial port name (e.g., 'COM3', '/dev/ttyUSB0').

    Returns:
        True if the port is available, False otherwise
    """
    try:
        # Try to open the port
        ser = serial.Serial(port, timeout=0.1)
        ser.close()
        return True
    except (serial.SerialException, OSError):
        # Port is not available
        return False
    
def reconnect(serial_conn: serial.Serial, max_attemps: int = 3) -> serial.Serial:
    """
    Try to reconnect a lost connection.

    Args:
        serial_conn: The serial connection to reconnect.
        max_attemps: Maximum number of reconnection attempts.

    Returns:
        A reconnected serial.Serial connection

    Raises:
        SerialConnectionError: If the reconnection fails after max attempts.
    """
    if serial_conn is None:
        raise SerialConnectionError("No serial connection to reconnect.")
    
    # Store original connection parameters
    port = serial_conn.port
    baudrate = serial_conn.baudrate
    timeout = serial_conn.timeout

    # Ensure the connection is closed before attempting to reconnect
    try:
        if serial_conn.is_open:
            serial_conn.close()
    except (serial.SerialException, OSError):
        pass # Ignore errors while closing

    # Try to reopen the connection
    return open_serial_connection(port, baudrate, timeout, max_attemps)

def wait_for_port(port: str, timeout: float = 10.0, interval: float = 0.5) -> bool:
    """
    Wait for a port to become available, up to a timeout.
    
    Args:
        port: Port name to wait for
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        
    Returns:
        True if port became available within timeout, False otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_port_available(port):
            return True
        time.sleep(interval)
    
    return False

def get_connection_status(serial_conn: serial.Serial) -> Dict[str, Any]:
    """
    Get the current status of a serial connection.
    
    Args:
        serial_conn: The serial connection to check
        
    Returns:
        A dictionary with connection status information
    """
    if serial_conn is None:
        return {"connected": False, "error": "Connection is None"}
    
    try:
        status = {
            "connected": serial_conn.is_open,
            "port": serial_conn.port,
            "baudrate": serial_conn.baudrate,
            "timeout": serial_conn.timeout,
            "in_waiting": 0,
            "out_waiting": 0
        }
        
        if serial_conn.is_open:
            status["in_waiting"] = serial_conn.in_waiting
            status["out_waiting"] = serial_conn.out_waiting
            
        return status
        
    except serial.SerialException as e:
        return {
            "connected": False,
            "error": str(e)
        }