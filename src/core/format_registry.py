"""
Format Registry System

Manages all available format processors and provides format detection
and processing capabilities.
"""
from typing import List, Optional, Dict, Any
import pandas as pd
from pathlib import Path
from .formats.base_processor import BaseFormatProcessor
from .formats.t12_processor import T12MonthlyFinancialProcessor
from .formats.standard_t12_processor import StandardT12Processor

class FormatRegistry:
    """
    Registry for managing format processors.
    
    Provides:
    - Format detection across all registered processors
    - Format processing with automatic processor selection
    - Format information and capabilities
    """
    
    def __init__(self):
        """Initialize registry with built-in processors."""
        self._processors: List[BaseFormatProcessor] = []
        self._register_built_in_processors()
    
    def _register_built_in_processors(self):
        """Register all built-in format processors."""
        # Register T12 Monthly Financial processor
        self.register_processor(T12MonthlyFinancialProcessor())
        # Register Standard T12 Workbook processor
        self.register_processor(StandardT12Processor())
    
    def register_processor(self, processor: BaseFormatProcessor):
        """
        Register a new format processor.
        
        Args:
            processor: Format processor instance
        """
        if not isinstance(processor, BaseFormatProcessor):
            raise ValueError("Processor must inherit from BaseFormatProcessor")
        
        # Check for duplicate format names
        existing_names = [p.format_name for p in self._processors]
        if processor.format_name in existing_names:
            raise ValueError(f"Processor with name '{processor.format_name}' already registered")
        
        self._processors.append(processor)
        print(f"Registered format processor: {processor.format_name}")
    
    def get_registered_formats(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered formats.
        
        Returns:
            List[Dict]: List of format information dictionaries
        """
        return [processor.get_format_info() for processor in self._processors]
    
    def detect_format(self, file_path: Path, sheet_name: Optional[str] = None) -> Optional[BaseFormatProcessor]:
        """
        Auto-detect the format of a file by trying each registered processor.
        
        Args:
            file_path: Path to the file
            sheet_name: Optional sheet name
            
        Returns:
            BaseFormatProcessor: The processor that can handle this format, or None
        """
        for processor in self._processors:
            try:
                if processor.can_process(file_path, sheet_name):
                    print(f"Detected format: {processor.format_name}")
                    return processor
            except Exception as e:
                print(f"Error checking format {processor.format_name}: {str(e)}")
                continue
        
        return None
    
    def process_file(self, file_path: Path, sheet_name: Optional[str] = None, 
                    format_name: Optional[str] = None) -> tuple[pd.DataFrame, BaseFormatProcessor]:
        """
        Process a file using automatic format detection or specified format.
        
        Args:
            file_path: Path to the file
            sheet_name: Optional sheet name
            format_name: Optional specific format name to use
            
        Returns:
            tuple: (processed_dataframe, processor_used)
            
        Raises:
            ValueError: If no suitable processor found or processing fails
        """
        processor = None
        
        if format_name:
            # Use specified format
            processor = self.get_processor_by_name(format_name)
            if not processor:
                raise ValueError(f"No processor registered for format: {format_name}")
        else:
            # Auto-detect format
            processor = self.detect_format(file_path, sheet_name)
            if not processor:
                available_formats = [p.format_name for p in self._processors]
                raise ValueError(f"No suitable format processor found. Available formats: {available_formats}")
        
        # Process the file
        try:
            df = processor.process(file_path, sheet_name)
            
            # Validate the result
            processor.validate_format(df)
            
            return df, processor
            
        except Exception as e:
            raise ValueError(f"Error processing file with {processor.format_name}: {str(e)}")
    
    def get_processor_by_name(self, format_name: str) -> Optional[BaseFormatProcessor]:
        """
        Get a processor by its format name.
        
        Args:
            format_name: Name of the format
            
        Returns:
            BaseFormatProcessor: The processor, or None if not found
        """
        for processor in self._processors:
            if processor.format_name == format_name:
                return processor
        return None
    
    def list_available_formats(self) -> List[str]:
        """
        Get list of available format names.
        
        Returns:
            List[str]: List of format names
        """
        return [processor.format_name for processor in self._processors]
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific format.
        
        Args:
            format_name: Name of the format
            
        Returns:
            Dict: Format information, or None if not found
        """
        processor = self.get_processor_by_name(format_name)
        return processor.get_format_info() if processor else None
    
    def validate_file_format(self, file_path: Path, expected_format: str, 
                           sheet_name: Optional[str] = None) -> bool:
        """
        Validate that a file matches the expected format.
        
        Args:
            file_path: Path to the file
            expected_format: Expected format name
            sheet_name: Optional sheet name
            
        Returns:
            bool: True if file matches expected format
        """
        processor = self.get_processor_by_name(expected_format)
        if not processor:
            return False
        
        return processor.can_process(file_path, sheet_name)

# Global registry instance
format_registry = FormatRegistry()

# Convenience functions for easy access
def detect_format(file_path: Path, sheet_name: Optional[str] = None) -> Optional[BaseFormatProcessor]:
    """Detect format using global registry."""
    return format_registry.detect_format(file_path, sheet_name)

def process_file(file_path: Path, sheet_name: Optional[str] = None, 
                format_name: Optional[str] = None) -> tuple[pd.DataFrame, BaseFormatProcessor]:
    """Process file using global registry."""
    return format_registry.process_file(file_path, sheet_name, format_name)

def list_available_formats() -> List[str]:
    """List available formats using global registry."""
    return format_registry.list_available_formats()

def get_format_info(format_name: str) -> Optional[Dict[str, Any]]:
    """Get format info using global registry."""
    return format_registry.get_format_info(format_name)
