"""
HTML parsing modules for different data types
"""
from .attendance_parser import AttendanceTableParser, AttendanceSubjectParser
from .timetable_parser import TimetableParser

__all__ = [
    'AttendanceTableParser',
    'AttendanceSubjectParser',
    'TimetableParser'
]
