"""
Shared file management for cross-mode file persistence.
Ensures uploaded files are available across both Production and Developer modes.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Any, Dict
import hashlib
import io


class SharedFileManager:
    """Manages file uploads and persistence across UI modes."""
    
    # Unified session state keys
    UPLOADED_FILE_KEY = 'shared_uploaded_file'
    PROCESSED_DF_KEY = 'shared_processed_df'
    FILE_METADATA_KEY = 'shared_file_metadata'
    
    @classmethod
    def get_uploaded_file(cls) -> Optional[Any]:
        """Get the currently uploaded file (available across all modes)."""
        return st.session_state.get(cls.UPLOADED_FILE_KEY)
    
    @classmethod
    def set_uploaded_file(cls, uploaded_file: Any) -> None:
        """Set the uploaded file (available across all modes)."""
        if uploaded_file is not None:
            st.session_state[cls.UPLOADED_FILE_KEY] = uploaded_file
            # Store metadata for change detection
            st.session_state[cls.FILE_METADATA_KEY] = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': getattr(uploaded_file, 'type', 'unknown')
            }
        else:
            cls.clear_uploaded_file()
    
    @classmethod
    def get_processed_df(cls) -> Optional[pd.DataFrame]:
        """Get the processed DataFrame (available across all modes)."""
        return st.session_state.get(cls.PROCESSED_DF_KEY)
    
    @classmethod
    def set_processed_df(cls, df: pd.DataFrame) -> None:
        """Set the processed DataFrame (available across all modes)."""
        st.session_state[cls.PROCESSED_DF_KEY] = df
    
    @classmethod
    def get_file_metadata(cls) -> Optional[Dict[str, Any]]:
        """Get file metadata for the current uploaded file."""
        return st.session_state.get(cls.FILE_METADATA_KEY)
    
    @classmethod
    def clear_uploaded_file(cls) -> None:
        """Clear the uploaded file and related data."""
        keys_to_clear = [
            cls.UPLOADED_FILE_KEY,
            cls.PROCESSED_DF_KEY,
            cls.FILE_METADATA_KEY,
            # Clear analysis results when file changes
            'ai_analysis_result',
            'ai_analysis_raw_response',
            'data_hash'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    @classmethod
    def has_uploaded_file(cls) -> bool:
        """Check if there's currently an uploaded file."""
        return cls.get_uploaded_file() is not None
    
    @classmethod
    def has_processed_data(cls) -> bool:
        """Check if there's currently processed data."""
        return cls.get_processed_df() is not None
    
    @classmethod
    def get_file_hash(cls, uploaded_file: Any) -> str:
        """Generate a hash for the uploaded file to detect changes."""
        if uploaded_file is None:
            return ""
        
        # Create hash from file name, size, and content sample
        hash_content = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # Add a sample of file content if available
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            # Read first 1KB for hash
            content_sample = uploaded_file.read(1024)
            uploaded_file.seek(0)  # Reset again
            
            if isinstance(content_sample, bytes):
                hash_content += content_sample.hex()
            else:
                hash_content += str(content_sample)
        except:
            # If we can't read content, just use metadata
            pass
        
        return hashlib.md5(hash_content.encode()).hexdigest()
    
    @classmethod
    def is_file_changed(cls, uploaded_file: Any) -> bool:
        """Check if the uploaded file has changed from the stored one."""
        if not cls.has_uploaded_file():
            return uploaded_file is not None
        
        if uploaded_file is None:
            return True
        
        stored_file = cls.get_uploaded_file()
        if stored_file is None:
            return True
        
        # Compare basic metadata
        if (uploaded_file.name != stored_file.name or 
            uploaded_file.size != stored_file.size):
            return True
        
        # If metadata matches, files are likely the same
        return False
    
    @classmethod
    def sync_legacy_session_state(cls) -> None:
        """Sync data from legacy session state keys to shared keys."""
        # Check for files from production mode
        if 'current_uploaded_file' in st.session_state and not cls.has_uploaded_file():
            cls.set_uploaded_file(st.session_state['current_uploaded_file'])
        
        if 'uploaded_file' in st.session_state and not cls.has_uploaded_file():
            cls.set_uploaded_file(st.session_state['uploaded_file'])
        
        # Check for files from developer mode
        if 'dev_uploaded_file' in st.session_state and not cls.has_uploaded_file():
            cls.set_uploaded_file(st.session_state['dev_uploaded_file'])
        
        # Check for processed data
        if 'processed_df' in st.session_state and not cls.has_processed_data():
            cls.set_processed_df(st.session_state['processed_df'])
    
    @classmethod
    def display_file_info(cls, uploaded_file: Optional[Any] = None) -> None:
        """Display information about the current uploaded file."""
        file_to_show = uploaded_file or cls.get_uploaded_file()
        
        if file_to_show is not None:
            metadata = cls.get_file_metadata()
            if metadata:
                st.success(f"✅ **{metadata['name']}** ({metadata['size']:,} bytes)")
                if metadata.get('type'):
                    st.info(f"**Type:** {metadata['type']}")
            else:
                st.success(f"✅ **{file_to_show.name}** ({file_to_show.size:,} bytes)")
                if hasattr(file_to_show, 'type'):
                    st.info(f"**Type:** {file_to_show.type}")
