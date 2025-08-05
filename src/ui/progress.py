"""
Progress tracking utilities for UI workflow
"""
import streamlit as st

def create_progress_tracker():
    """Create a progress tracking system"""
    if 'processing_steps' not in st.session_state:
        st.session_state.processing_steps = {
            'file_upload': False,
            'file_validation': False, 
            'data_processing': False,
            'kpi_generation': False,
            'ai_analysis': False
        }
    return st.session_state.processing_steps

def update_progress(step_name, status=True):
    """Update progress for a specific step"""
    if 'processing_steps' in st.session_state:
        st.session_state.processing_steps[step_name] = status

def display_progress():
    """Display progress indicators"""
    progress = st.session_state.get('processing_steps', {})
    
    st.subheader("🔄 Processing Progress")
    
    steps = [
        ('file_upload', '📁 File Upload'),
        ('file_validation', '✅ File Validation'),
        ('data_processing', '⚙️ Data Processing'),
        ('kpi_generation', '📊 KPI Generation'),
        ('ai_analysis', '🤖 AI Analysis')
    ]
    
    for step_key, step_label in steps:
        status = progress.get(step_key, False)
        if status:
            st.success(f"{step_label} ✓")
        else:
            st.info(f"{step_label} ⏳")
