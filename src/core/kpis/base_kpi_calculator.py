"""
Base KPI Calculator - Abstract base class for all KPI calculators

This provides the interface that all KPI calculators must implement
to ensure consistent behavior across different data formats.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

class BaseKPICalculator(ABC):
    """
    Abstract base class for all KPI calculators.
    
    Each KPI calculator must implement:
    - KPI calculation logic specific to the format
    - Trend analysis for the format's data structure
    - Ratio calculations relevant to the format
    - Standardized summary output
    """
    
    def __init__(self, format_name: str, calculator_description: str):
        """
        Initialize the base KPI calculator.
        
        Args:
            format_name: Name of the data format this calculator handles
            calculator_description: Human-readable description of this calculator
        """
        self.format_name = format_name
        self.calculator_description = calculator_description
        self.calculation_issues = []
    
    @abstractmethod
    def calculate_kpis(self, df: pd.DataFrame) -> str:
        """
        Calculate KPIs and return formatted summary string.
        
        Args:
            df: Processed DataFrame from format processor
            
        Returns:
            str: Formatted KPI summary for AI analysis
        """
        pass
    
    @abstractmethod
    def get_key_metrics(self) -> List[str]:
        """
        Get list of key metrics this calculator focuses on.
        
        Returns:
            List[str]: List of key metric names
        """
        pass
    
    @abstractmethod
    def calculate_trends(self, df: pd.DataFrame) -> List[str]:
        """
        Calculate trend analysis for this format.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            List[str]: List of trend analysis strings
        """
        pass
    
    @abstractmethod
    def calculate_ratios(self, df: pd.DataFrame) -> List[str]:
        """
        Calculate performance ratios for this format.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            List[str]: List of ratio calculation strings
        """
        pass
    
    def get_metric_value(self, data: pd.DataFrame, metric_name: str) -> Optional[float]:
        """
        Get value for a specific metric from the data.
        
        Args:
            data: DataFrame with metric data
            metric_name: Name of the metric to find
            
        Returns:
            float: Metric value, or None if not found
        """
        try:
            # Try exact match first
            exact_match = data[data['Metric'] == metric_name]['Value']
            if len(exact_match) > 0:
                return exact_match.iloc[0]
            
            # Try partial match if exact match fails
            partial_match = data[data['Metric'].str.contains(
                metric_name, case=False, na=False, regex=False
            )]['Value']
            if len(partial_match) > 0:
                return partial_match.iloc[0]
            
            return None
        except Exception as e:
            self.add_calculation_issue(f"Error getting metric '{metric_name}': {str(e)}")
            return None
    
    def get_latest_period_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get data for the latest time period (non-YTD).
        
        Args:
            df: Processed DataFrame
            
        Returns:
            pd.DataFrame: Data for latest period
        """
        # Filter out YTD data and get latest period
        non_ytd_data = df[~df["IsYTD"]].copy()
        if non_ytd_data.empty:
            return pd.DataFrame()
        
        # Find the latest period
        if 'PeriodParsed' in non_ytd_data.columns:
            latest_period = non_ytd_data["PeriodParsed"].max()
            return non_ytd_data[non_ytd_data["PeriodParsed"] == latest_period]
        else:
            # Fallback to last available data
            return non_ytd_data.tail(len(non_ytd_data) // 2)  # Rough estimate
    
    def get_ytd_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get YTD (Year-To-Date) data.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            pd.DataFrame: YTD data
        """
        return df[df["IsYTD"]].copy()
    
    def format_currency(self, value: float) -> str:
        """
        Format a numeric value as currency.
        
        Args:
            value: Numeric value
            
        Returns:
            str: Formatted currency string
        """
        if value is None:
            return "N/A"
        return f"${value:,.2f}"
    
    def format_percentage(self, value: float) -> str:
        """
        Format a numeric value as percentage.
        
        Args:
            value: Numeric value (as decimal, e.g., 0.15 for 15%)
            
        Returns:
            str: Formatted percentage string
        """
        if value is None:
            return "N/A"
        return f"{value:.1f}%"
    
    def add_calculation_issue(self, issue: str):
        """Add a calculation issue to the list."""
        self.calculation_issues.append(issue)
    
    def get_calculation_issues(self) -> List[str]:
        """Get list of calculation issues."""
        return self.calculation_issues.copy()
    
    def clear_calculation_issues(self):
        """Clear the calculation issues list."""
        self.calculation_issues = []
    
    def log_calculation_issues(self):
        """Print calculation issues to console."""
        if self.calculation_issues:
            print(f"[{self.format_name} KPI Calculator Issues]")
            for issue in self.calculation_issues:
                print(f"- {issue}")
    
    def get_calculator_info(self) -> Dict[str, Any]:
        """
        Get information about this KPI calculator.
        
        Returns:
            Dict with calculator metadata
        """
        return {
            "format_name": self.format_name,
            "description": self.calculator_description,
            "key_metrics": self.get_key_metrics(),
            "calculator_class": self.__class__.__name__
        }
    
    def validate_data_structure(self, df: pd.DataFrame) -> bool:
        """
        Validate that the DataFrame has the expected structure for KPI calculation.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_columns = ["Metric", "Value", "IsYTD"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.add_calculation_issue(f"Missing required columns: {missing_columns}")
            return False
        
        if df.empty:
            self.add_calculation_issue("DataFrame is empty")
            return False
        
        return True
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """
        Get metric categories for this format.
        Should be overridden by specific calculators.
        
        Returns:
            Dict[str, List[str]]: Categories and their metrics
        """
        return {}
    
    def group_metrics_by_category(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Group available metrics by category.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dict[str, List[str]]: Categories with found metrics and values
        """
        categories = self.get_metric_categories()
        grouped_metrics = {}
        all_metrics = df["Metric"].unique()
        used_metrics = set()
        
        for category, patterns in categories.items():
            category_metrics = []
            for pattern in patterns:
                for metric in all_metrics:
                    if (pattern.lower().replace(" ", "") in metric.lower().replace(" ", "") 
                        and metric not in used_metrics):
                        value = self.get_metric_value(df, metric)
                        if value is not None:
                            formatted_value = self.format_currency(value)
                            category_metrics.append(f"• {metric}: {formatted_value}")
                            used_metrics.add(metric)
            
            if category_metrics:
                grouped_metrics[category] = category_metrics
        
        # Handle uncategorized metrics
        remaining_metrics = [m for m in all_metrics if m not in used_metrics]
        if remaining_metrics:
            other_metrics = []
            for metric in remaining_metrics:
                value = self.get_metric_value(df, metric)
                if value is not None:
                    formatted_value = self.format_currency(value)
                    other_metrics.append(f"• {metric}: {formatted_value}")
            
            if other_metrics:
                grouped_metrics["OTHER_METRICS"] = other_metrics
        
        return grouped_metrics
