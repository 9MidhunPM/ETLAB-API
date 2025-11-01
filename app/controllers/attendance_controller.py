"""
Attendance controller - subject-wise attendance summary
"""
from flask import Blueprint, request
from bs4 import BeautifulSoup
import logging
from app.services.attendance_service import AttendanceService
from app.parsers.attendance_parser import AttendanceSubjectParser
from app.utils.auth_utils import extract_token
from app.utils.response_utils import (
    create_success_response,
    create_unauthorized_response,
    create_token_expired_response,
    create_error_response
)

logger = logging.getLogger(__name__)

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    """
    Get subject-wise attendance data
    Shows attendance percentage for each subject
    
    Query Parameters:
        - semester: Semester number (default: 5)
    """
    try:
        # Step 1: Extract and validate token
        token = extract_token(request.headers.get('Authorization'))
        if not token:
            return create_unauthorized_response()
        
        # Step 2: Get semester parameter
        semester = request.args.get('semester', '5')
        
        # Step 3: Fetch attendance HTML
        html = AttendanceService.fetch_attendance_subjects(token, semester)
        
        # Step 4: Check for session expiry
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title and 'login' in title.get_text().lower():
            return create_token_expired_response()
        
        # Step 5: Parse attendance data
        attendance_data = AttendanceSubjectParser.parse(html, semester)
        
        # Step 6: Build response
        response_data = AttendanceService.build_attendance_subjects_response(
            attendance_data, semester
        )
        
        # Step 7: Handle empty data
        if not attendance_data:
            response_data['message'] = "Attendance table not found or no data available"
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching attendance: {e}", exc_info=True)
        return create_error_response(
            f"Error fetching attendance data: {str(e)}",
            "SERVER_ERROR",
            status_code=500
        )
