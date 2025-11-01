import logging
from typing import Optional
from bs4 import BeautifulSoup
from app.config.config import config
from app.services.http_service import http_service

logger = logging.getLogger(__name__)

class DataContextService:
    """Service for retrieving relevant context data for AI queries"""
    
    def get_relevant_context(self, context_type: str, token: str) -> str:
        """
        Get relevant context data based on type
        
        Args:
            context_type: Type of context needed (results, attendance, timetable, profile, general)
            token: Session token for authentication
            
        Returns:
            Formatted context string
        """
        try:
            context_type = context_type.lower() if context_type else "general"
            
            if context_type == "results":
                return self._get_results_context(token)
            elif context_type == "attendance":
                return self._get_attendance_context(token)
            elif context_type == "timetable":
                return self._get_timetable_context(token)
            elif context_type == "profile":
                return self._get_profile_context(token)
            else:
                return self._get_general_context(token)
                
        except Exception as e:
            logger.error(f"Error getting context for type {context_type}: {e}")
            return "Unable to retrieve context data at this time."
    
    def _get_results_context(self, token: str) -> str:
        """Get academic results context"""
        try:
            html = http_service.get(f"{config.base_url}/ktuacademics/student/results", token)
            soup = BeautifulSoup(html, 'html.parser')
            
            context = ["ACADEMIC RESULTS DATA:\\n\\n"]
            
            # Parse results data
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text().lower()
                if any(keyword in table_text for keyword in ['result', 'grade', 'marks', 'score']):
                    context.append("Results Table:\\n")
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            context.append("- ")
                            for cell in cells:
                                context.append(f"{cell.get_text().strip()} | ")
                            context.append("\\n")
                    context.append("\\n")
            
            return "".join(context)
            
        except Exception as e:
            logger.error(f"Error getting results context: {e}")
            return "Results data unavailable."
    
    def _get_attendance_context(self, token: str) -> str:
        """Get attendance context"""
        try:
            html = http_service.get(f"{config.base_url}/ktuacademics/student/attendance", token)
            soup = BeautifulSoup(html, 'html.parser')
            
            context = ["ATTENDANCE DATA:\\n\\n"]
            
            # Parse attendance data
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text().lower()
                if any(keyword in table_text for keyword in ['attendance', 'present', 'absent']):
                    context.append("Attendance Table:\\n")
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            context.append("- ")
                            for cell in cells:
                                context.append(f"{cell.get_text().strip()} | ")
                            context.append("\\n")
                    context.append("\\n")
            
            return "".join(context)
            
        except Exception as e:
            logger.error(f"Error getting attendance context: {e}")
            return "Attendance data unavailable."
    
    def _get_timetable_context(self, token: str) -> str:
        """Get timetable context"""
        try:
            html = http_service.get(f"{config.base_url}/student/timetable?format=csv&yt0=", token)
            
            context = ["TIMETABLE DATA:\\n\\n"]
            
            # Check if it's CSV data or HTML
            if html.strip().startswith('<'):
                # It's HTML, parse accordingly
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('title')
                if title and 'login' in title.get_text().lower():
                    return "Timetable access denied - please login."
                context.append("Timetable format may have changed or be unavailable.\\n")
            else:
                # It's CSV data
                context.append("CSV Timetable Data:\\n")
                lines = html.strip().split('\\n')[:20]  # Limit to prevent too much data
                for line in lines:
                    if line.strip():
                        context.append(f"- {line.strip()}\\n")
            
            return "".join(context)
            
        except Exception as e:
            logger.error(f"Error getting timetable context: {e}")
            return "Timetable data unavailable."
    
    def _get_profile_context(self, token: str) -> str:
        """Get profile context"""
        try:
            html = http_service.get(f"{config.base_url}/student/profile", token)
            soup = BeautifulSoup(html, 'html.parser')
            
            context = ["PROFILE DATA:\\n\\n"]
            
            # Parse profile information
            # Look for common profile elements
            profile_elements = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and 'profile' in x.lower())
            
            if not profile_elements:
                # Try to find any structured data
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) == 2:  # Key-value pairs
                            key = cells[0].get_text().strip()
                            value = cells[1].get_text().strip()
                            if key and value:
                                context.append(f"- {key}: {value}\\n")
            else:
                for element in profile_elements:
                    text = element.get_text().strip()
                    if text:
                        context.append(f"- {text}\\n")
            
            return "".join(context)
            
        except Exception as e:
            logger.error(f"Error getting profile context: {e}")
            return "Profile data unavailable."
    
    def _get_general_context(self, token: str) -> str:
        """Get general context (combination of available data)"""
        try:
            context = []
            
            # Try to get a bit of each type of data
            try:
                results = self._get_results_context(token)
                if "unavailable" not in results.lower():
                    context.append(results[:500])  # Limit size
                    context.append("\\n")
            except:
                pass
            
            try:
                attendance = self._get_attendance_context(token)
                if "unavailable" not in attendance.lower():
                    context.append(attendance[:300])  # Smaller limit for general context
                    context.append("\\n")
            except:
                pass
            
            if not context:
                return "General academic context unavailable at this time."
            
            return "".join(context)
            
        except Exception as e:
            logger.error(f"Error getting general context: {e}")
            return "General context unavailable."

# Global instance
data_context_service = DataContextService()