"""
Timetable controller - class schedule retrieval
"""
from flask import Blueprint, request
import logging
from app.config.config import config
from app.services.http_service import http_service
from app.parsers.timetable_parser import TimetableParser
from app.utils.auth_utils import extract_token
from app.utils.response_utils import (
    create_success_response,
    create_unauthorized_response,
    create_error_response
)

logger = logging.getLogger(__name__)

timetable_bp = Blueprint('timetable', __name__)


@timetable_bp.route('/api/timetable', methods=['GET'])
def get_timetable():
    """
    Get timetable data in CSV format and convert to JSON
    """
    try:
        # Step 1: Extract and validate token
        token = extract_token(request.headers.get('Authorization'))
        if not token:
            return create_unauthorized_response()
        
        # Step 2: Fetch timetable data
        url = f"{config.base_url}/student/timetable?format=csv&yt0="
        csv_data = http_service.get(url, token)
        
        # Step 3: Parse timetable
        timetable_data = TimetableParser.parse(csv_data)
        
        return create_success_response(timetable_data)
        
    except Exception as e:
        logger.error(f"Error fetching timetable: {e}", exc_info=True)
        return create_error_response(
            f"Error fetching timetable data: {str(e)}",
            "SERVER_ERROR",
            status_code=500
        )
