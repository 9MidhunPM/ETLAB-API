"""
Attendance data parser - handles HTML parsing for attendance tables
"""
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AttendanceTableParser:
    """
    Parser for day-by-day attendance table with period-level details
    """
    
    @staticmethod
    def parse(html: str) -> Dict:
        """
        Parse attendance table HTML into structured data
        
        Args:
            html: HTML content from attendance page
        
        Returns:
            Dictionary with dates and period-level attendance
        """
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        
        dates_data = []
        
        for table in tables:
            # Look for the attendance table with period columns
            headers = table.find_all('th')
            header_texts = [h.get_text().strip() for h in headers]
            
            # Check if this is the attendance table (has Period columns)
            if any('Period' in h for h in header_texts) and 'Date' in header_texts:
                dates_data = AttendanceTableParser._parse_attendance_table(table)
                break
        
        return dates_data
    
    @staticmethod
    def _parse_attendance_table(table) -> List[Dict]:
        """
        Parse individual attendance table rows
        
        Args:
            table: BeautifulSoup table element
        
        Returns:
            List of date entries with period data
        """
        dates_data = []
        rows = table.find_all('tr')
        
        # Debug first row structure
        if len(rows) > 1:
            AttendanceTableParser._log_first_row_debug(rows[1])
        
        # Skip header row
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 2:
                continue
            
            # First cell is the date
            date_text = cells[0].get_text().strip()
            
            # Skip empty or summary rows
            if not date_text or date_text.lower() in ['', 'total', 'percentage']:
                continue
            
            date_entry = {
                'date': date_text,
                'periods': AttendanceTableParser._parse_periods(cells[1:])
            }
            
            # Only add if we have period data
            if date_entry['periods']:
                dates_data.append(date_entry)
        
        return dates_data
    
    @staticmethod
    def _parse_periods(cells) -> List[Dict]:
        """
        Parse period cells for a single date
        
        Args:
            cells: List of BeautifulSoup cell elements (excluding date cell)
        
        Returns:
            List of period data dictionaries
        """
        periods = []
        
        for period_idx, cell in enumerate(cells, start=1):
            period_data = AttendanceTableParser._parse_period_cell(cell, period_idx)
            periods.append(period_data)
        
        return periods
    
    @staticmethod
    def _parse_period_cell(cell, period_idx: int) -> Dict:
        """
        Parse a single period cell to determine status and subject
        
        Args:
            cell: BeautifulSoup cell element
            period_idx: Period number
        
        Returns:
            Dictionary with period, status, and subject
        """
        # Get ALL possible color indicators
        cell_style = cell.get('style', '')
        cell_class = ' '.join(cell.get('class', []))
        cell_bgcolor = cell.get('bgcolor', '')
        cell_text = cell.get_text().strip()
        
        # Comprehensive color detection
        color_indicators = cell_style + ' ' + cell_class + ' ' + cell_bgcolor
        color_lower = color_indicators.lower()
        
        # Present indicators (green shades)
        is_present = any([
            'green' in color_lower,
            '#00ff00' in color_lower,
            '#0f0' in color_lower,
            'rgb(0, 255, 0)' in color_lower,
            'rgb(0,255,0)' in color_lower,
            '#90ee90' in color_lower,  # light green
            '#00ff7f' in color_lower,  # spring green
            'success' in color_lower,  # Bootstrap success class
            'present' in color_lower   # Common class name
        ])
        
        # Absent indicators (red shades)
        is_absent = any([
            'red' in color_lower,
            '#ff0000' in color_lower,
            '#f00' in color_lower,
            'rgb(255, 0, 0)' in color_lower,
            'rgb(255,0,0)' in color_lower,
            '#dc143c' in color_lower,  # crimson
            '#ff6b6b' in color_lower,  # light red
            'danger' in color_lower,   # Bootstrap danger class
            'absent' in color_lower    # Common class name
        ])
        
        # Determine status and extract subject
        if is_present:
            status = 'present'
            subject = ' '.join(cell_text.split()) if cell_text and cell_text != '-' else ''
        elif is_absent:
            status = 'absent'
            subject = ' '.join(cell_text.split()) if cell_text and cell_text != '-' else ''
        elif cell_text and cell_text != '-':
            # Has text but no clear color - assume present with subject
            status = 'present'
            subject = ' '.join(cell_text.split())
        else:
            # Empty or just dash - no class scheduled
            status = 'no_class'
            subject = ''
        
        return {
            'period': period_idx,
            'status': status,
            'subject': subject
        }
    
    @staticmethod
    def _log_first_row_debug(row):
        """Log debug info for first data row"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) > 1:
                logger.info("=" * 60)
                logger.info(f"FIRST DATA ROW - Date: {cells[0].get_text().strip()}")
                logger.info(f"Period 1 Cell HTML: {str(cells[1])[:300]}")
                logger.info(f"Period 1 Attributes: style='{cells[1].get('style', '')}' class='{cells[1].get('class', [])}' bgcolor='{cells[1].get('bgcolor', '')}'")
                if len(cells) > 2:
                    logger.info(f"Period 2 Cell HTML: {str(cells[2])[:300]}")
                    logger.info(f"Period 2 Attributes: style='{cells[2].get('style', '')}' class='{cells[2].get('class', [])}' bgcolor='{cells[2].get('bgcolor', '')}'")
                logger.info("=" * 60)
        except Exception as e:
            logger.warning(f"Debug logging failed: {e}")
    
    @staticmethod
    def calculate_summary(dates_data: List[Dict]) -> Dict:
        """
        Calculate attendance summary statistics
        
        Args:
            dates_data: List of date entries with periods
        
        Returns:
            Summary dictionary with counts and percentage
        """
        total_periods = 0
        present_count = 0
        absent_count = 0
        no_class_count = 0
        
        for date_entry in dates_data:
            for period in date_entry['periods']:
                total_periods += 1
                if period['status'] == 'present':
                    present_count += 1
                elif period['status'] == 'absent':
                    absent_count += 1
                elif period['status'] == 'no_class':
                    no_class_count += 1
        
        # Calculate percentage excluding no_class periods
        attended_periods = present_count + absent_count
        percentage = round((present_count / attended_periods * 100), 2) if attended_periods > 0 else 0
        
        return {
            'total_periods': total_periods,
            'present': present_count,
            'absent': absent_count,
            'no_class': no_class_count,
            'percentage': percentage
        }


class AttendanceSubjectParser:
    """
    Parser for subject-wise attendance summary
    """
    
    @staticmethod
    def parse(html: str, semester: str) -> Dict:
        """
        Parse subject-wise attendance from HTML
        
        Args:
            html: HTML content from attendance page
            semester: Semester number
        
        Returns:
            Dictionary with attendance data per subject
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find attendance table
        table = soup.find('table', class_='items')
        
        if not table:
            # Try to find any table that might contain attendance data
            tables = soup.find_all('table')
            for t in tables:
                table_text = t.get_text().lower()
                if any(keyword in table_text for keyword in ['attendance', 'present', 'absent', 'subject']):
                    table = t
                    break
        
        if not table:
            return []
        
        return AttendanceSubjectParser._parse_attendance_table(table)
    
    @staticmethod
    def _parse_attendance_table(table) -> List[Dict]:
        """
        Parse subject-wise attendance table
        
        Args:
            table: BeautifulSoup table element
        
        Returns:
            List of subject attendance data
        """
        attendance_data = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return []
        
        # First row should be headers (subject names)
        header_row = rows[0]
        headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
        
        # Find the data row(s) - usually the second row contains the student's attendance
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text().strip() for cell in cells]
            
            # Skip first few columns (usually ID, Roll No, Name, etc.)
            for col_idx, cell_text in enumerate(cell_texts):
                # Look for attendance pattern: "present/total (percentage%)"
                if '/' in cell_text and col_idx >= 3:  # Skip first 3 columns
                    subject_data = AttendanceSubjectParser._parse_attendance_cell(
                        cell_text, headers, col_idx
                    )
                    if subject_data:
                        attendance_data.append(subject_data)
        
        return attendance_data
    
    @staticmethod
    def _parse_attendance_cell(cell_text: str, headers: List[str], col_idx: int) -> Optional[Dict]:
        """
        Parse individual attendance cell (e.g., "46/49 (94%)")
        
        Args:
            cell_text: Cell text content
            headers: Table headers list
            col_idx: Column index
        
        Returns:
            Dictionary with subject attendance data or None
        """
        import re
        
        # Extract attendance data
        match = re.search(r'(\d+)/(\d+)', cell_text)
        if not match:
            return None
        
        present = int(match.group(1))
        total = int(match.group(2))
        
        # Try to extract percentage
        percentage_match = re.search(r'(\d+)%', cell_text)
        if percentage_match:
            percentage = float(percentage_match.group(1))
        else:
            percentage = round((present / total * 100), 2) if total > 0 else 0
        
        # Get subject name from header
        subject_name = headers[col_idx] if col_idx < len(headers) else f"Subject_{col_idx}"
        
        return {
            'subject': subject_name,
            'present': present,
            'total': total,
            'percentage': percentage
        }
