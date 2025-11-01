"""
Date and time utilities
"""
from typing import Union


# Month name to number mapping
MONTH_MAP = {
    'jan': '1', 'january': '1',
    'feb': '2', 'february': '2',
    'mar': '3', 'march': '3',
    'apr': '4', 'april': '4',
    'may': '5',
    'jun': '6', 'june': '6',
    'jul': '7', 'july': '7',
    'aug': '8', 'august': '8',
    'sep': '9', 'september': '9',
    'oct': '10', 'october': '10',
    'nov': '11', 'november': '11',
    'dec': '12', 'december': '12'
}

# Reverse mapping
NUMBER_TO_MONTH = {
    '1': 'January', '2': 'February', '3': 'March',
    '4': 'April', '5': 'May', '6': 'June',
    '7': 'July', '8': 'August', '9': 'September',
    '10': 'October', '11': 'November', '12': 'December'
}


def convert_month_to_number(month_param: Union[str, int], default: str = '10') -> str:
    """
    Convert month name or number to numeric string
    
    Args:
        month_param: Month as name (e.g., "Oct", "October") or number (e.g., 10, "10")
        default: Default month number if conversion fails
    
    Returns:
        Month as numeric string (1-12)
    
    Examples:
        >>> convert_month_to_number("Oct")
        '10'
        >>> convert_month_to_number(10)
        '10'
        >>> convert_month_to_number("October")
        '10'
    """
    month_str = str(month_param)
    
    # Check if already numeric
    if month_str.isdigit():
        month_num = int(month_str)
        if 1 <= month_num <= 12:
            return month_str
    
    # Try to convert from name
    if month_str.lower() in MONTH_MAP:
        return MONTH_MAP[month_str.lower()]
    
    # Return default if conversion fails
    return default


def get_month_name(month_number: Union[str, int]) -> str:
    """
    Get full month name from number
    
    Args:
        month_number: Month number (1-12)
    
    Returns:
        Full month name
    
    Examples:
        >>> get_month_name(10)
        'October'
        >>> get_month_name('10')
        'October'
    """
    month_str = str(month_number)
    return NUMBER_TO_MONTH.get(month_str, 'Unknown')
