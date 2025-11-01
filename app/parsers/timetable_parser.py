"""
Timetable parser - handles HTML/CSV parsing for timetable data
"""
from typing import Dict, List
from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class TimetableParser:
    """
    Parser for timetable data in CSV or HTML format
    """
    
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    @staticmethod
    def parse(data: str) -> Dict:
        """
        Parse timetable data (CSV or HTML)
        
        Args:
            data: CSV or HTML content
        
        Returns:
            Dictionary with timetable schedule
        """
        # Check if data is HTML or CSV
        if data.strip().startswith('<'):
            return TimetableParser._parse_html(data)
        else:
            return TimetableParser._parse_csv(data)
    
    @staticmethod
    def _parse_csv(csv_data: str) -> Dict:
        """
        Parse CSV timetable data into structured format
        
        Args:
            csv_data: CSV content string
        
        Returns:
            Dictionary with schedule data
        """
        try:
            csv_file = StringIO(csv_data)
            csv_reader = csv.reader(csv_file)
            rows = list(csv_reader)
            
            if not rows:
                return {
                    "message": "No timetable data found",
                    "schedule": TimetableParser._get_empty_schedule()
                }
            
            # Initialize schedule structure
            schedule = TimetableParser._get_empty_schedule()
            
            # Find headers and day columns
            header_info = TimetableParser._find_csv_headers(rows)
            
            if header_info['format'] == 'days_as_columns':
                schedule = TimetableParser._parse_days_as_columns(
                    rows, header_info['header_row_idx'],
                    header_info['time_col_idx'], header_info['day_col_indices']
                )
            elif header_info['format'] == 'days_as_rows':
                schedule = TimetableParser._parse_days_as_rows(rows)
            
            total_periods = sum(len(schedule[day]) for day in schedule)
            
            return {
                "message": "Timetable retrieved successfully",
                "schedule": schedule,
                "total_periods": total_periods
            }
            
        except Exception as e:
            logger.error(f"Error parsing CSV timetable: {e}", exc_info=True)
            return {
                "message": "Error parsing timetable data",
                "error": str(e),
                "raw_preview": csv_data[:500] + "..." if len(csv_data) > 500 else csv_data,
                "schedule": TimetableParser._get_empty_schedule()
            }
    
    @staticmethod
    def _parse_html(html: str) -> Dict:
        """
        Parse HTML timetable (fallback method)
        
        Args:
            html: HTML content
        
        Returns:
            Dictionary with error message
        """
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        
        if title and 'login' in title.get_text().lower():
            return {
                "message": "Session expired",
                "schedule": TimetableParser._get_empty_schedule()
            }
        
        return {
            "message": "Timetable data not available or endpoint format has changed",
            "schedule": TimetableParser._get_empty_schedule()
        }
    
    @staticmethod
    def _get_empty_schedule() -> OrderedDict:
        """Get empty schedule structure"""
        schedule = OrderedDict()
        for day in TimetableParser.DAYS:
            schedule[day] = []
        return schedule
    
    @staticmethod
    def _find_csv_headers(rows: List[List[str]]) -> Dict:
        """
        Find headers and determine CSV format
        
        Args:
            rows: CSV rows
        
        Returns:
            Dictionary with header information
        """
        header_row_idx = -1
        time_col_idx = -1
        day_col_indices = {}
        csv_format = 'unknown'
        
        for i, row in enumerate(rows):
            row_lower = [cell.lower().strip() for cell in row]
            
            # Check if this row contains day names
            for j, cell in enumerate(row_lower):
                for day in TimetableParser.DAYS:
                    if day.lower() in cell:
                        day_col_indices[day] = j
            
            # Check if this row contains "time" column
            if any('time' in cell or 'period' in cell for cell in row_lower):
                header_row_idx = i
                for j, cell in enumerate(row_lower):
                    if 'time' in cell or 'period' in cell:
                        time_col_idx = j
                        break
            
            if header_row_idx >= 0:
                csv_format = 'days_as_columns'
                break
        
        # If no headers found, check for days as rows format
        if csv_format == 'unknown':
            for row in rows:
                if row and row[0].strip().lower() in [d.lower() for d in TimetableParser.DAYS]:
                    csv_format = 'days_as_rows'
                    break
        
        return {
            'format': csv_format,
            'header_row_idx': header_row_idx,
            'time_col_idx': time_col_idx,
            'day_col_indices': day_col_indices
        }
    
    @staticmethod
    def _parse_days_as_columns(rows: List[List[str]], header_row_idx: int,
                               time_col_idx: int, day_col_indices: Dict) -> OrderedDict:
        """
        Parse CSV where days are columns
        
        Args:
            rows: CSV rows
            header_row_idx: Header row index
            time_col_idx: Time column index
            day_col_indices: Day column indices
        
        Returns:
            Schedule dictionary
        """
        schedule = TimetableParser._get_empty_schedule()
        
        for i in range(header_row_idx + 1, len(rows)):
            row = rows[i]
            
            # Skip empty rows
            if all(cell.strip() == '' for cell in row):
                continue
            
            # Get time slot
            time_slot = row[time_col_idx].strip() if time_col_idx >= 0 and time_col_idx < len(row) else ""
            
            # Extract subjects for each day
            for day, col_idx in day_col_indices.items():
                if col_idx < len(row):
                    subject_info = row[col_idx].strip()
                    
                    if subject_info and subject_info.lower() not in ['', '-', 'break', 'lunch']:
                        period = {
                            'time': time_slot,
                            'subject': subject_info
                        }
                        schedule[day].append(period)
        
        return schedule
    
    @staticmethod
    def _parse_days_as_rows(rows: List[List[str]]) -> OrderedDict:
        """
        Parse CSV where days are rows
        
        Args:
            rows: CSV rows
        
        Returns:
            Schedule dictionary
        """
        schedule = TimetableParser._get_empty_schedule()
        
        for row in rows:
            if not row or all(cell.strip() == '' for cell in row):
                continue
            
            # Check if this row starts with a day name
            if len(row) > 0 and row[0].strip().lower() in [d.lower() for d in TimetableParser.DAYS]:
                current_day = next(d for d in TimetableParser.DAYS if d.lower() == row[0].strip().lower())
                
                # Parse all periods in this row (columns 1 onwards)
                for j in range(1, len(row)):
                    cell = row[j].strip()
                    
                    if not cell:
                        continue
                    
                    # Handle free periods, breaks, and lunch
                    if cell.lower() in ['free period', 'break', 'lunch', '-']:
                        period = {
                            'period': j,
                            'subject': cell,
                            'type': 'free'
                        }
                        schedule[current_day].append(period)
                        continue
                    
                    # Clean up HTML tags and newlines
                    cell_clean = cell.replace('<br/>', ' - ').replace('<br>', ' - ')
                    cell_clean = cell_clean.replace('\n', ' ').replace('\r', ' ')
                    cell_clean = ' '.join(cell_clean.split())
                    
                    period = TimetableParser._parse_period_cell(cell_clean, j)
                    schedule[current_day].append(period)
        
        return schedule
    
    @staticmethod
    def _parse_period_cell(cell_text: str, period_num: int) -> Dict:
        """
        Parse individual period cell
        
        Args:
            cell_text: Cell content
            period_num: Period number
        
        Returns:
            Period dictionary
        """
        period = {
            'period': period_num,
            'subject': cell_text
        }
        
        # Try to parse structured format: "CODE - NAME [ Type ] TEACHER"
        lines = cell_text.split(' - ')
        if len(lines) >= 2:
            period['code'] = lines[0].strip()
            period['name'] = lines[1].split('[')[0].strip() if '[' in lines[1] else lines[1].strip()
            
            # Extract type if present
            if '[' in cell_text and ']' in cell_text:
                type_match = cell_text[cell_text.find('[')+1:cell_text.find(']')]
                period['type'] = type_match.strip()
            
            # Teacher is usually after the last bracket or hyphen
            parts = cell_text.replace('[', '-').replace(']', '-').split('-')
            if len(parts) > 2:
                period['teacher'] = parts[-1].strip()
        
        return period
