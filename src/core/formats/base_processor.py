"""
Base Format Processor - Abstract base class for all data format processors

This provides the interface that all format processors must implement
to ensure consistent behavior across different data formats.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path

class BaseFormatProcessor(ABC):
    """
    Abstract base class for all format processors.
    
    Each format processor must implement:
    - Format detection logic
    - Data preprocessing logic  
    - Format validation
    - Metadata extraction
    """
    
    def __init__(self, format_name: str, format_description: str):
        """
        Initialize the base processor.
        
        Args:
            format_name: Unique name for this format (e.g., "T12_Monthly_Financial")
            format_description: Human-readable description of this format
        """
        self.format_name = format_name
        self.format_description = format_description
        self.quality_issues = []
    
    @abstractmethod
    def can_process(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """
        Determine if this processor can handle the given file.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Optional sheet name to check
            
        Returns:
            bool: True if this processor can handle the file format
        """
        pass
    
    @abstractmethod
    def process(self, file_path: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Process the file and return standardized DataFrame.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Optional sheet name to process
            
        Returns:
            pd.DataFrame: Standardized long-format DataFrame with columns:
                - Sheet: Sheet name
                - Metric: Metric/line item name
                - Period: Time period (Month, Week, etc.)
                - PeriodParsed: Parsed datetime
                - IsYTD: Boolean flag for YTD data
                - Value: Numeric value
                - Additional format-specific columns
        """
        pass
    
    @abstractmethod
    def validate_format(self, df: pd.DataFrame) -> bool:
        """
        Validate that the processed DataFrame meets format expectations.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        pass
    
    @abstractmethod
    def get_expected_metrics(self) -> List[str]:
        """
        Get list of expected metrics for this format.
        
        Returns:
            List[str]: List of expected metric names or patterns
        """
        pass
    
    def get_format_info(self) -> Dict[str, Any]:
        """
        Get information about this format processor.
        
        Returns:
            Dict with format metadata
        """
        return {
            "name": self.format_name,
            "description": self.format_description,
            "expected_metrics": self.get_expected_metrics(),
            "processor_class": self.__class__.__name__
        }
    
    def get_quality_issues(self) -> List[str]:
        """
        Get list of data quality issues found during processing.
        
        Returns:
            List[str]: List of quality issue descriptions
        """
        return self.quality_issues.copy()
    
    def clear_quality_issues(self):
        """Clear the quality issues list."""
        self.quality_issues = []
    
    def add_quality_issue(self, issue: str):
        """Add a quality issue to the list."""
        self.quality_issues.append(issue)
    
    def log_quality_issues(self):
        """Print quality issues to console."""
        if self.quality_issues:
            print(f"[{self.format_name} Data Quality Checks]")
            for issue in self.quality_issues:
                print(f"- {issue}")
    
    @staticmethod
    def parse_money(x) -> Optional[float]:
        """
        Convert Excel-style money strings to float.
        Handles formats like: $1,234.56, ($1,234.56), 1234.56
        
        Args:
            x: Value to parse
            
        Returns:
            float or None: Parsed monetary value
        """
        if pd.isna(x):
            return None
        
        s = str(x).strip()
        neg = s.startswith("(") and s.endswith(")")
        s = s.strip("()$").replace(",", "")
        
        try:
            return -float(s) if neg else float(s)
        except:
            return None
    
    def get_standardized_columns(self) -> List[str]:
        """
        Get the standardized column names that all processors should return.
        
        Returns:
            List[str]: Standard column names
        """
        return [
            "Sheet",
            "Metric", 
            "Period",
            "PeriodParsed",
            "IsYTD",
            "Value"
        ]
