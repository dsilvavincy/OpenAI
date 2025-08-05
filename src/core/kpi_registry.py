"""
KPI Registry System

Manages all available KPI calculators and provides KPI calculation
capabilities for different data formats.
"""
from typing import List, Optional, Dict, Any
import pandas as pd
from .kpis.base_kpi_calculator import BaseKPICalculator
from .kpis.t12_kpi_calculator import T12MonthlyFinancialKPICalculator

class KPIRegistry:
    """
    Registry for managing KPI calculators.
    
    Provides:
    - KPI calculation for different formats
    - Calculator management and information
    - Standardized KPI output interface
    """
    
    def __init__(self):
        """Initialize registry with built-in KPI calculators."""
        self._calculators: Dict[str, BaseKPICalculator] = {}
        self._register_built_in_calculators()
    
    def _register_built_in_calculators(self):
        """Register all built-in KPI calculators."""
        # Register T12 Monthly Financial KPI calculator
        self.register_calculator(T12MonthlyFinancialKPICalculator())
    
    def register_calculator(self, calculator: BaseKPICalculator):
        """
        Register a new KPI calculator.
        
        Args:
            calculator: KPI calculator instance
        """
        if not isinstance(calculator, BaseKPICalculator):
            raise ValueError("Calculator must inherit from BaseKPICalculator")
        
        # Check for duplicate format names
        if calculator.format_name in self._calculators:
            raise ValueError(f"Calculator for format '{calculator.format_name}' already registered")
        
        self._calculators[calculator.format_name] = calculator
        print(f"Registered KPI calculator: {calculator.format_name}")
    
    def get_registered_calculators(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered KPI calculators.
        
        Returns:
            List[Dict]: List of calculator information dictionaries
        """
        return [calc.get_calculator_info() for calc in self._calculators.values()]
    
    def calculate_kpis(self, df: pd.DataFrame, format_name: str) -> str:
        """
        Calculate KPIs for a specific format.
        
        Args:
            df: Processed DataFrame
            format_name: Name of the format to calculate KPIs for
            
        Returns:
            str: Formatted KPI summary
            
        Raises:
            ValueError: If no calculator found for format
        """
        calculator = self.get_calculator_by_format(format_name)
        if not calculator:
            available_formats = list(self._calculators.keys())
            raise ValueError(f"No KPI calculator found for format: {format_name}. Available: {available_formats}")
        
        try:
            return calculator.calculate_kpis(df)
        except Exception as e:
            raise ValueError(f"Error calculating KPIs with {format_name} calculator: {str(e)}")
    
    def get_calculator_by_format(self, format_name: str) -> Optional[BaseKPICalculator]:
        """
        Get a KPI calculator by format name.
        
        Args:
            format_name: Name of the format
            
        Returns:
            BaseKPICalculator: The calculator, or None if not found
        """
        return self._calculators.get(format_name)
    
    def list_available_formats(self) -> List[str]:
        """
        Get list of available format names.
        
        Returns:
            List[str]: List of format names
        """
        return list(self._calculators.keys())
    
    def get_calculator_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific calculator.
        
        Args:
            format_name: Name of the format
            
        Returns:
            Dict: Calculator information, or None if not found
        """
        calculator = self.get_calculator_by_format(format_name)
        return calculator.get_calculator_info() if calculator else None
    
    def get_key_metrics(self, format_name: str) -> Optional[List[str]]:
        """
        Get key metrics for a specific format.
        
        Args:
            format_name: Name of the format
            
        Returns:
            List[str]: Key metrics, or None if format not found
        """
        calculator = self.get_calculator_by_format(format_name)
        return calculator.get_key_metrics() if calculator else None
    
    def calculate_trends(self, df: pd.DataFrame, format_name: str) -> List[str]:
        """
        Calculate trends for a specific format.
        
        Args:
            df: Processed DataFrame
            format_name: Name of the format
            
        Returns:
            List[str]: Trend analysis strings
        """
        calculator = self.get_calculator_by_format(format_name)
        if not calculator:
            return []
        
        try:
            return calculator.calculate_trends(df)
        except Exception as e:
            print(f"Error calculating trends for {format_name}: {str(e)}")
            return []
    
    def calculate_ratios(self, df: pd.DataFrame, format_name: str) -> List[str]: 
        """
        Calculate ratios for a specific format.
        
        Args:
            df: Processed DataFrame
            format_name: Name of the format
            
        Returns:
            List[str]: Ratio calculation strings
        """
        calculator = self.get_calculator_by_format(format_name)
        if not calculator:
            return []
        
        try:
            latest_data = calculator.get_latest_period_data(df)
            return calculator.calculate_ratios(latest_data)
        except Exception as e:
            print(f"Error calculating ratios for {format_name}: {str(e)}")
            return []
    
    def validate_calculator_data(self, df: pd.DataFrame, format_name: str) -> bool:
        """
        Validate that DataFrame is suitable for KPI calculation.
        
        Args:
            df: DataFrame to validate
            format_name: Name of the format
            
        Returns:
            bool: True if data is valid for calculation
        """
        calculator = self.get_calculator_by_format(format_name)
        if not calculator:
            return False
        
        return calculator.validate_data_structure(df)
    
    def get_calculation_issues(self, format_name: str) -> List[str]:
        """
        Get calculation issues from the last KPI calculation.
        
        Args:
            format_name: Name of the format
            
        Returns:
            List[str]: List of calculation issues
        """
        calculator = self.get_calculator_by_format(format_name)
        return calculator.get_calculation_issues() if calculator else []

# Global KPI registry instance
kpi_registry = KPIRegistry()

# Convenience functions for easy access
def calculate_kpis(df: pd.DataFrame, format_name: str) -> str:
    """Calculate KPIs using global registry."""
    return kpi_registry.calculate_kpis(df, format_name)

def list_available_kpi_formats() -> List[str]:
    """List available KPI calculator formats using global registry."""
    return kpi_registry.list_available_formats()

def get_key_metrics(format_name: str) -> Optional[List[str]]:
    """Get key metrics using global registry."""
    return kpi_registry.get_key_metrics(format_name)

def calculate_trends(df: pd.DataFrame, format_name: str) -> List[str]:
    """Calculate trends using global registry."""
    return kpi_registry.calculate_trends(df, format_name)

def calculate_ratios(df: pd.DataFrame, format_name: str) -> List[str]:
    """Calculate ratios using global registry.""" 
    return kpi_registry.calculate_ratios(df, format_name)
