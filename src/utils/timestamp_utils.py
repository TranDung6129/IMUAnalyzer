"""
Timestamp handling utilities for IMU sensor data.

This module provides functions for generating and converting timestamps
in various formats for IMU data processing with UTC support.
"""
# timestamp_utils.py
import time
from datetime import datetime, timezone, timedelta
from typing import Union, Optional, Dict, Any

def generate_timestamp(mode: str = 'realtime', 
                       packet_count: Optional[int] = None,
                       time_step: float = 0.01,
                       device_time: Optional[datetime] = None,
                       start_time: Optional[float] = None,
                       utc_offset: Optional[int] = None) -> Union[str, float, int]:
    """
    Generate a timestamp based on the specified mode.
    
    Args:
        mode: Timestamp mode ('realtime', 'packet', 'chiptime', 'unix')
        packet_count: Packet counter for packet-based timestamps
        time_step: Time step between packets in seconds
        device_time: Device time from sensor (for 'chiptime' mode)
        start_time: Start time in seconds since epoch
        utc_offset: UTC offset in hours (e.g., +8 for UTC+8)
        
    Returns:
        Timestamp in the requested format
    """
    # Apply UTC offset if provided
    tz = timezone.utc if utc_offset == 0 else timezone(timedelta(hours=utc_offset)) if utc_offset is not None else None
    
    if mode == 'chiptime':
        # Use device time if available
        if device_time:
            # Adjust time if UTC offset is specified
            if tz and device_time.tzinfo is None:
                device_time = device_time.replace(tzinfo=tz)
            return device_time.strftime("%H:%M:%S.%f")[:-3]  # Format as HH:MM:SS.mmm
        else:
            # Fall back to packet count if no device time
            return str(packet_count) if packet_count is not None else "0"
        
    elif mode == 'realtime':
        # Current time with millisecond precision
        if tz:
            current_time = datetime.now(tz)
        else:
            current_time = datetime.now()
        return current_time.strftime("%H:%M:%S.%f")[:-3]  # Format as HH:MM:SS.mmm
        
    elif mode == 'packet':
        # Simple packet counter
        return str(packet_count) if packet_count is not None else "0"
        
    elif mode == 'unix':
        # Unix timestamp (seconds since epoch)
        if start_time and packet_count is not None:
            # Relative time from start
            return start_time + (packet_count * time_step)
        else:
            # Current time
            if tz:
                return datetime.now(tz).timestamp()
            else:
                return time.time()
    else:
        # Default to current time
        if tz:
            return datetime.now(tz).timestamp()
        else:
            return time.time()

def parse_timestamp(timestamp_str: str, format_str: Optional[str] = None, 
                   utc_offset: Optional[int] = None) -> datetime:
    """
    Parse a timestamp string into a datetime object.
    
    Args:
        timestamp_str: Timestamp string to parse
        format_str: Format string for parsing (optional)
        utc_offset: UTC offset in hours (e.g., +8 for UTC+8)
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If the timestamp cannot be parsed
    """
    # Define timezone based on UTC offset
    tz = timezone.utc if utc_offset == 0 else timezone(timedelta(hours=utc_offset)) if utc_offset is not None else None
    
    if format_str:
        try:
            dt = datetime.strptime(timestamp_str, format_str)
            if tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            pass
    
    # Try common formats if no format string is provided or it failed
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",  # 2023-01-01 12:34:56.789
        "%Y-%m-%d %H:%M:%S",     # 2023-01-01 12:34:56
        "%H:%M:%S.%f",           # 12:34:56.789
        "%H:%M:%S",              # 12:34:56
        "%Y%m%d%H%M%S",          # 20230101123456
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            if tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            continue
    
    # Try to parse as Unix timestamp (float)
    try:
        timestamp = float(timestamp_str)
        dt = datetime.fromtimestamp(timestamp)
        if tz and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt
    except ValueError:
        pass
    
    raise ValueError(f"Could not parse timestamp: {timestamp_str}")

def convert_timestamp(timestamp: Union[str, datetime, float, int], 
                     output_format: str = 'datetime',
                     utc_offset: Optional[int] = None) -> Union[str, datetime, float, int]:
    """
    Convert a timestamp from one format to another.
    
    Args:
        timestamp: Input timestamp (string, datetime, float/int for Unix timestamp)
        output_format: Desired output format
            ('datetime', 'string', 'unix', 'isoformat', 'rfc3339')
        utc_offset: UTC offset in hours (e.g., +8 for UTC+8)
        
    Returns:
        Converted timestamp in the requested format
    """
    # Define timezone based on UTC offset
    tz = timezone.utc if utc_offset == 0 else timezone(timedelta(hours=utc_offset)) if utc_offset is not None else None
    
    # Convert input to datetime
    if isinstance(timestamp, str):
        dt = parse_timestamp(timestamp, utc_offset=utc_offset)
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
        if tz and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
    elif isinstance(timestamp, datetime):
        dt = timestamp
        if tz and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
    else:
        raise TypeError(f"Unsupported timestamp type: {type(timestamp)}")
    
    # Convert to output format
    if output_format == 'datetime':
        return dt
    elif output_format == 'string':
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    elif output_format == 'unix':
        return dt.timestamp()
    elif output_format == 'isoformat':
        return dt.isoformat()
    elif output_format == 'rfc3339':
        # RFC 3339 format (used in JSON, etc.)
        # Always use UTC for RFC3339
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def get_timestamp_from_packet(packet_data: bytes, byte_offset: int, 
                            byte_length: int, format_type: str,
                            utc_offset: Optional[int] = None) -> datetime:
    """
    Extract a timestamp from packet data.
    
    Args:
        packet_data: Raw packet data
        byte_offset: Offset to timestamp data in bytes
        byte_length: Length of timestamp data in bytes
        format_type: Type of timestamp format in packet
            ('unix', 'witmotion', 'milliseconds', etc.)
        utc_offset: UTC offset in hours (e.g., +8 for UTC+8)
        
    Returns:
        Datetime object representing the timestamp
    """
    # Define timezone based on UTC offset
    tz = timezone.utc if utc_offset == 0 else timezone(timedelta(hours=utc_offset)) if utc_offset is not None else None
    
    if format_type == 'unix':
        # Unix timestamp (seconds since epoch)
        if byte_length == 4:
            timestamp = int.from_bytes(packet_data[byte_offset:byte_offset+4], byteorder='little')
            dt = datetime.fromtimestamp(timestamp)
        elif byte_length == 8:
            timestamp = int.from_bytes(packet_data[byte_offset:byte_offset+8], byteorder='little')
            dt = datetime.fromtimestamp(timestamp / 1000)  # Milliseconds
        else:
            dt = datetime.now()
            
        if tz and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt
    
    elif format_type == 'witmotion':
        # WitMotion timestamp format (year, month, day, hour, minute, second, millisecond)
        year = 2000 + packet_data[byte_offset]
        month = packet_data[byte_offset+1]
        day = packet_data[byte_offset+2]
        hour = packet_data[byte_offset+3]
        minute = packet_data[byte_offset+4]
        second = packet_data[byte_offset+5]
        millisecond = int.from_bytes(packet_data[byte_offset+6:byte_offset+8], byteorder='little')
        
        try:
            dt = datetime(year, month, day, hour, minute, second, millisecond * 1000)
            if tz and dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            # Return current time if the packet contains invalid date/time
            if tz:
                return datetime.now(tz)
            else:
                return datetime.now()
    
    elif format_type == 'milliseconds':
        # Milliseconds counter
        millis = int.from_bytes(packet_data[byte_offset:byte_offset+byte_length], byteorder='little')
        # Convert to a relative time from epoch
        dt = datetime.fromtimestamp(millis / 1000.0)
        if tz and dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt
    
    # Default to current time if format not recognized
    if tz:
        return datetime.now(tz)
    else:
        return datetime.now()