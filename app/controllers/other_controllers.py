from flask import Blueprint, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import logging
import re
from app.config.config import config
from app.services.http_service import http_service
from app.models.dto import ApiResponse

logger = logging.getLogger(__name__)

# Create blueprints for each controller
web_bp = Blueprint('web', __name__)
profile_bp = Blueprint('profile', __name__)
results_bp = Blueprint('results', __name__)
status_bp = Blueprint('status', __name__)
logout_bp = Blueprint('logout', __name__)

def extract_token(auth_header):
    """Extract token from Authorization header"""
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

# Web Controller Routes
@web_bp.route('/')
def index():
    """Serve index.html for root path"""
    return send_from_directory('../static', 'index.html')

@web_bp.route('/dashboard')
def dashboard():
    """Serve index.html for dashboard path"""
    return send_from_directory('../static', 'index.html')

# Profile Controller
@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile information"""
    try:
        auth_header = request.headers.get('Authorization')
        token = extract_token(auth_header)
        
        if not token:
            return jsonify(ApiResponse("Authorization token is required").to_dict()), 401
        
        url = f"{config.base_url}/student/profile"
        html = http_service.get(url, token)
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        
        if title and 'login' in title.get_text().lower():
            return jsonify(ApiResponse("Token expired. Please login again.").to_dict()), 401
        
        profile_data = {}
        
        # Extract profile information from the page
        # Look for tables or structured data
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        profile_data[key.lower().replace(' ', '_')] = value
        
        # If no structured data found, extract any available text
        if not profile_data:
            content = soup.find('body')
            if content:
                text = content.get_text()
                profile_data['raw_content'] = text[:500] + "..." if len(text) > 500 else text
        
        return jsonify({
            "success": True,
            "profile": profile_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        return jsonify(ApiResponse(f"Error fetching profile data: {str(e)}").to_dict()), 500

# Results Controller
@results_bp.route('/api/results', methods=['GET'])
def get_results():
    """Get academic results"""
    try:
        auth_header = request.headers.get('Authorization')
        token = extract_token(auth_header)
        
        if not token:
            return jsonify(ApiResponse("Authorization token is required").to_dict()), 401
        
        semester = request.args.get('semester', '5')
        url = f"{config.base_url}/ktuacademics/student/results"
        html = http_service.get(url, token)
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title and 'login' in title.get_text().lower():
            return jsonify(ApiResponse("Token expired. Please login again.").to_dict()), 401
        
        results_data = []
        
        # Find results tables
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            table_text = table.get_text().lower()
            
            if any(keyword in table_text for keyword in ['result', 'grade', 'marks', 'subject', 'score']):
                rows = table.find_all('tr')
                
                # Get headers
                if len(rows) > 0:
                    header_row = rows[0]
                    headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
                
                for row_idx, row in enumerate(rows[1:] if len(rows) > 1 else rows, start=1):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    
                    if len(cells) >= 2:
                        subject_data = {}
                        
                        # Extract data based on column headers
                        for j, cell_text in enumerate(cell_texts):
                            if not cell_text or j >= len(headers):
                                continue
                            
                            header = headers[j].lower()
                            
                            # Subject column
                            if 'subject' in header and cell_text:
                                subject_data['subject'] = cell_text
                            
                            # Semester column
                            elif 'semester' in header and cell_text:
                                subject_data['semester'] = cell_text
                            
                            # Exam/Assignment/Project type
                            elif any(x in header for x in ['exam', 'assignment', 'project', 'class project', 'title']) and cell_text:
                                subject_data['type'] = cell_text
                            
                            # Maximum marks
                            elif 'maximum' in header and cell_text.replace('.', '').isdigit():
                                try:
                                    subject_data['max_marks'] = int(cell_text)
                                except:
                                    pass
                            
                            # Marks obtained
                            elif 'obtained' in header and cell_text:
                                # Check if it's a number or status like "Results not published"
                                if cell_text.replace('.', '').isdigit():
                                    try:
                                        subject_data['marks'] = int(cell_text)
                                    except:
                                        pass
                                else:
                                    subject_data['status'] = cell_text
                        
                        if 'subject' in subject_data and subject_data['subject']:
                            results_data.append(subject_data)
        
        return jsonify({
            "success": True,
            "results": results_data,
            "semester": semester
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        return jsonify(ApiResponse(f"Error fetching results data: {str(e)}").to_dict()), 500

@results_bp.route('/api/end-semester-results', methods=['GET'])
def get_end_semester_results():
    """Get KTU end semester examination results"""
    try:
        auth_header = request.headers.get('Authorization')
        token = extract_token(auth_header)
        
        if not token:
            return jsonify(ApiResponse("Authorization token is required").to_dict()), 401
        
        # End semester results listing page
        url = f"{config.base_url}/universityexam/student/examresult"
        html = http_service.get(url, token)
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title and 'login' in title.get_text().lower():
            return jsonify(ApiResponse("Token expired. Please login again.").to_dict()), 401
        
        # Find all "View Result" links/buttons to get individual result pages
        exam_results = []
        
        # Look for result cards or links
        result_links = soup.find_all('a', href=True)
        for link in result_links:
            href = link.get('href', '')
            # Look for view result links
            if 'viewresult' in href.lower() or 'examresult' in href.lower():
                # Fetch individual result page
                try:
                    if not href.startswith('http'):
                        result_url = f"{config.base_url}{href}" if href.startswith('/') else f"{config.base_url}/{href}"
                    else:
                        result_url = href
                    
                    result_html = http_service.get(result_url, token)
                    result_soup = BeautifulSoup(result_html, 'html.parser')
                    
                    # Extract exam details
                    exam_data = {
                        'exam_name': '',
                        'degree': '',
                        'semester': '',
                        'academic_year': '',
                        'month': '',
                        'year': '',
                        'subjects': [],
                        'earned_credit': 0,
                        'sgpa': 0.0,
                        'cgpa': 0.0
                    }
                    
                    # Extract exam metadata from the page
                    # Look for metadata in various formats
                    
                    # Method 1: Look in table rows with label-value pairs
                    all_rows = result_soup.find_all('tr')
                    for row in all_rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].get_text().strip()
                            value = cells[1].get_text().strip()
                            
                            label_lower = label.lower()
                            
                            if 'name of exam' in label_lower:
                                exam_data['exam_name'] = value
                            elif 'degree' in label_lower and not exam_data['degree']:
                                exam_data['degree'] = value
                            elif 'semester' in label_lower and not exam_data['semester']:
                                exam_data['semester'] = value
                            elif 'academic year' in label_lower:
                                exam_data['academic_year'] = value
                            elif 'month' in label_lower and 'academic' not in label_lower:
                                exam_data['month'] = value
                            elif label_lower == 'year:' or (label_lower == 'year' and 'academic' not in label_lower):
                                exam_data['year'] = value
                    
                    # Method 2: Look in breadcrumbs or page title
                    if not exam_data['exam_name']:
                        # Check page title or h2/h3 tags
                        title_tags = result_soup.find_all(['h1', 'h2', 'h3', 'title'])
                        for tag in title_tags:
                            text = tag.get_text().strip()
                            if 'semester' in text.lower() and 'exam' in text.lower():
                                exam_data['exam_name'] = text
                                break
                        
                        # Check breadcrumb or navigation
                        if not exam_data['exam_name']:
                            breadcrumbs = result_soup.find_all(['a', 'span'], href=True)
                            for bc in breadcrumbs:
                                text = bc.get_text().strip()
                                if 'semester' in text.lower() and len(text) > 20:
                                    exam_data['exam_name'] = text
                                    break
                    
                    # Method 3: Extract from exam_name if still empty
                    if exam_data['exam_name']:
                        name = exam_data['exam_name']
                        
                        # Extract semester from name if not set
                        if not exam_data['semester']:
                            import re
                            semester_match = re.search(r'(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ist|IInd|IIIrd|IVth|Vth|VIth|VIIth|VIIIth)\s+Semester', name, re.IGNORECASE)
                            if semester_match:
                                exam_data['semester'] = semester_match.group(0)
                        
                        # Extract degree from name if not set
                        if not exam_data['degree']:
                            if 'B.Tech' in name or 'B Tech' in name or 'BTech' in name:
                                exam_data['degree'] = 'BTech KTU'
                            elif 'M.Tech' in name or 'M Tech' in name or 'MTech' in name:
                                exam_data['degree'] = 'MTech KTU'
                        
                        # Extract year and month from name if not set
                        if not exam_data['year'] or not exam_data['month']:
                            import re
                            # Look for patterns like "December 2024" or "May 2025"
                            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', name)
                            if date_match:
                                if not exam_data['month']:
                                    exam_data['month'] = date_match.group(1)
                                if not exam_data['year']:
                                    exam_data['year'] = date_match.group(2)
                        
                        # Extract academic year if not set (format: 2024 Admission or 2024-2025)
                        if not exam_data['academic_year']:
                            import re
                            # Look for "(2024 Admission)" or "2024-2025"
                            admission_match = re.search(r'\((\d{4})\s+Admission\)', name)
                            if admission_match:
                                year = admission_match.group(1)
                                # Convert to academic year format
                                exam_data['academic_year'] = f"{year}-{int(year)+1}"
                            else:
                                year_match = re.search(r'(\d{4})-(\d{4})', name)
                                if year_match:
                                    exam_data['academic_year'] = f"{year_match.group(1)}-{year_match.group(2)}"
                    
                    # Find the results table
                    tables = result_soup.find_all('table')
                    
                    for table in tables:
                        rows = table.find_all('tr')
                        
                        # Find header row
                        header_row = None
                        for row in rows:
                            cells = row.find_all(['th', 'td'])
                            cell_texts = [cell.get_text().strip().lower() for cell in cells]
                            if any(keyword in ' '.join(cell_texts) for keyword in ['course code', 'course name', 'grade', 'slot']):
                                header_row = row
                                break
                        
                        if not header_row:
                            continue
                        
                        # Get headers
                        headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
                        
                        # Parse data rows
                        for row in rows:
                            if row == header_row:
                                continue
                                
                            cells = row.find_all('td')
                            if len(cells) < 2:
                                continue
                            
                            cell_texts = [cell.get_text().strip() for cell in cells]
                            row_text = ' '.join(cell_texts)
                            
                            # Check for SGPA row
                            if 'SGPA' in row_text:
                                # SGPA value is usually the last numeric cell or second column
                                for text in reversed(cell_texts):
                                    if text.replace('.', '').replace(',', '').isdigit():
                                        try:
                                            exam_data['sgpa'] = float(text.replace(',', '.'))
                                            break
                                        except:
                                            pass
                                continue
                            
                            # Check for CGPA row
                            if 'CGPA' in row_text:
                                # CGPA value is usually the last numeric cell or second column
                                for text in reversed(cell_texts):
                                    if text.replace('.', '').replace(',', '').isdigit():
                                        try:
                                            exam_data['cgpa'] = float(text.replace(',', '.'))
                                            break
                                        except:
                                            pass
                                continue
                            
                            # Check for Earned Credit row
                            if 'Earned Credit' in row_text:
                                # Credit value is usually the last numeric cell or second column
                                for text in reversed(cell_texts):
                                    if text.isdigit():
                                        try:
                                            exam_data['earned_credit'] = int(text)
                                            break
                                        except:
                                            pass
                                continue
                            
                            # Skip other summary/header rows
                            if any(x in row_text.lower() for x in ['course code', 'course name', 'no', 'slot']) and len(cell_texts) > 4:
                                continue
                            
                            # Parse subject data
                            subject_data = {}
                            
                            for j, cell_text in enumerate(cell_texts):
                                if j >= len(headers):
                                    break
                                
                                header = headers[j].lower()
                                
                                # Slot/No column
                                if 'slot' in header or header == 'no':
                                    subject_data['slot'] = cell_text
                                
                                # Course Code
                                elif 'course code' in header or 'code' in header:
                                    subject_data['code'] = cell_text
                                
                                # Course Name
                                elif 'course name' in header or 'name' in header:
                                    subject_data['name'] = cell_text
                                
                                # Grade
                                elif 'grade' in header:
                                    subject_data['grade'] = cell_text
                                
                                # Credit
                                elif 'credit' in header:
                                    try:
                                        subject_data['credit'] = int(cell_text) if cell_text.isdigit() else 0
                                    except:
                                        pass
                                
                                # Pass Status
                                elif 'pass' in header or 'status' in header:
                                    subject_data['status'] = cell_text
                            
                            # Only add if we have at least course code or name
                            if subject_data.get('code') or subject_data.get('name'):
                                exam_data['subjects'].append(subject_data)
                    
                    # Only add if we found subjects
                    if exam_data['subjects']:
                        exam_results.append(exam_data)
                
                except Exception as e:
                    logger.error(f"Error fetching individual result: {e}")
                    continue
        
        return jsonify({
            "success": True,
            "exams": exam_results,
            "total_exams": len(exam_results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching end semester results: {e}")
        return jsonify(ApiResponse(f"Error fetching end semester results: {str(e)}").to_dict()), 500

# Status Controller
@status_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get application status"""
    return jsonify({
        "status": "running",
        "message": "ETLabsHR API is running successfully",
        "version": "1.0.0"
    }), 200

# Logout Controller
@logout_bp.route('/api/logout', methods=['GET'])
def logout():
    """Logout user (clear session)"""
    try:
        # In a stateless API, logout mainly involves client-side token removal
        return jsonify(ApiResponse("Logout successful").to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify(ApiResponse("Error during logout").to_dict()), 500