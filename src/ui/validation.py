"""
File validation utilities for T12 uploads
"""
import streamlit as st

def validate_uploaded_file(uploaded_file):
    """Validate uploaded T12 file"""
    validation_results = {
        "is_valid": False,
        "messages": [],
        "warnings": []
    }
    
    # Check file extension
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        validation_results["messages"].append("❌ Invalid file format. Please upload an Excel file (.xlsx or .xls)")
        return validation_results
    
    # Check file size (max 50MB)
    file_content = uploaded_file.getvalue()  # Get file content without moving file pointer
    file_size = len(file_content)
    
    if file_size > 50 * 1024 * 1024:  # 50MB
        validation_results["messages"].append("❌ File too large. Maximum size is 50MB")
        return validation_results
    
    if file_size < 1024:  # 1KB
        validation_results["messages"].append("❌ File too small. This doesn't appear to be a valid T12 file")
        return validation_results
    
    validation_results["is_valid"] = True
    validation_results["messages"].append("✅ File format and size validation passed")
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        validation_results["warnings"].append("⚠️ Large file detected. Processing may take longer")
    
    return validation_results
