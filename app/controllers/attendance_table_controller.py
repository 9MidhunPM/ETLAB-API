"""
Attendance table controller - day-by-day attendance with period details
"""
from flask import Blueprint, request
from bs4 import BeautifulSoup
import logging
from app.services.attendance_service import AttendanceService
from app.parsers.attendance_parser import AttendanceTableParser
from app.utils.auth_utils import extract_token
from app.utils.date_utils import convert_month_to_number
from app.utils.response_utils import (
    create_success_response,
    create_unauthorized_response,
    create_token_expired_response,
    create_error_response
)

logger = logging.getLogger(__name__)

attendance_table_bp = Blueprint('attendance_table', __name__)


@attendance_table_bp.route('/api/attendance-table', methods=['GET'])
def get_attendance_table():
    """
    Get detailed attendance table with date-wise records
    Shows which periods were present/absent for each date
    
    Query Parameters:
        - semester: Semester number (default: 3)
        - month: Month name or number (e.g., "Oct", "October", "10")
        - year: Year (default: 2025)
    """
    try:
        # Step 1: Extract and validate token
        token = extract_token(request.headers.get('Authorization'))
        if not token:
            return create_unauthorized_response()
        
        # Step 2: Get query parameters
        semester = request.args.get('semester', '3')
        month_param = request.args.get('month', '10')
        year = request.args.get('year', '2025')
        
        # Step 3: Convert month to numeric format
        month = convert_month_to_number(month_param, default='10')
        
        # Step 4: Fetch attendance HTML
        html = AttendanceService.fetch_attendance_table(token, semester, month, year)
        
        # Step 5: Check for session expiry
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title and 'login' in title.get_text().lower():
            return create_token_expired_response()
        
        # Step 6: Parse attendance table
        dates_data = AttendanceTableParser.parse(html)
        
        # Step 7: Build response
        response_data = AttendanceService.build_attendance_table_response(
            dates_data, semester, month, month_param, year
        )
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching attendance table: {e}", exc_info=True)
        return create_error_response(
            f"Error fetching attendance table: {str(e)}",
            "SERVER_ERROR",
            status_code=500
        )
