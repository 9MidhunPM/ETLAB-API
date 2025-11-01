"""
Attendance service - handles attendance data fetching and processing
"""
import logging
from typing import Dict, List
from app.config.config import config
from app.services.http_service import http_service
from app.parsers.attendance_parser import AttendanceTableParser, AttendanceSubjectParser
from app.utils.date_utils import convert_month_to_number

logger = logging.getLogger(__name__)


class AttendanceService:
    """
    Service for fetching and processing attendance data
    """
    
    @staticmethod
    def fetch_attendance_table(token: str, semester: str, month: str, year: str) -> str:
        """
        Fetch attendance table HTML from server
        
        Args:
            token: Authentication token
            semester: Semester number
            month: Month number (1-12)
            year: Year
        
        Returns:
            HTML content
        """
        url = f"{config.base_url}/ktuacademics/student/attendance"
        
        # POST with form data (etlab expects numeric month)
        form_data = {
            'month': month,
            'year': year,
            'semester': semester
        }
        
        response = http_service.post(url, data=form_data, token=token)
        return response.text if hasattr(response, 'text') else response.content.decode('utf-8')
    
    @staticmethod
    def fetch_attendance_subjects(token: str, semester: str) -> str:
        """
        Fetch subject-wise attendance HTML
        
        Args:
            token: Authentication token
            semester: Semester number
        
        Returns:
            HTML content
        """
        url = f"{config.base_url}/ktuacademics/student/viewattendancesubject/{semester}"
        return http_service.get(url, token)
    
    @staticmethod
    def build_attendance_table_response(dates_data: List[Dict], semester: str,
                                       month: str, month_requested: str, year: str) -> Dict:
        """
        Build complete attendance table response
        
        Args:
            dates_data: Parsed dates data
            semester: Semester number
            month: Numeric month
            month_requested: Original month parameter
            year: Year
        
        Returns:
            Complete response dictionary
        """
        summary = AttendanceTableParser.calculate_summary(dates_data)
        
        return {
            'semester': semester,
            'month': month,
            'month_requested': month_requested,
            'year': year,
            'dates': dates_data,
            'summary': summary
        }
    
    @staticmethod
    def build_attendance_subjects_response(attendance_data: List[Dict], semester: str) -> Dict:
        """
        Build subject-wise attendance response
        
        Args:
            attendance_data: Parsed attendance data
            semester: Semester number
        
        Returns:
            Response dictionary
        """
        response_data = {
            'attendance': attendance_data,
            'semester': semester
        }
        
        if attendance_data:
            # Calculate overall attendance
            total_percentage = sum(item.get('percentage', 0) for item in attendance_data)
            avg_percentage = total_percentage / len(attendance_data)
            response_data['overall_percentage'] = round(avg_percentage, 2)
        
        return response_data
