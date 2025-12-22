"""
Question Store - SQLite-based persistence for user-edited investigative questions.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path("data/question_overrides.db")


class QuestionStore:
    """
    Manages persistence of user-edited investigative questions.
    Uses SQLite for efficient storage and retrieval.
    """
    
    def __init__(self):
        """Initialize the database connection and create tables if needed."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        logger.info(f"QuestionStore initialized with database: {DB_PATH}")
    
    def _init_db(self):
        """Create the database schema if it doesn't exist."""
        cursor = self.conn.cursor()
        # Table for question edits
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_key TEXT NOT NULL,
                section TEXT NOT NULL,
                category TEXT NOT NULL,
                metric TEXT NOT NULL,
                questions TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(property_key, section, category, metric)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_property_key 
            ON question_overrides(property_key)
        """)
        
        # Table for full analysis results (History)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_analysis (
                property_key TEXT PRIMARY KEY,
                analysis_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    @staticmethod
    def make_key(property_name: str, report_period: str) -> str:
        """
        Create a unique key for a property/period combination.
        
        Args:
            property_name: Name of the property
            report_period: Period string (e.g., "Nov 2024" or "2024-11")
            
        Returns:
            Unique key string like "Property Name|2024-11"
        """
        # Normalize period to YYYY-MM format if possible
        try:
            from dateutil import parser
            dt = parser.parse(report_period)
            period_normalized = dt.strftime("%Y-%m")
        except:
            period_normalized = report_period
        
        return f"{property_name}|{period_normalized}"
    
    def get_overrides(self, property_key: str) -> Dict[str, Any]:
        """
        Get all question overrides for a property/period.
        
        Args:
            property_key: Key from make_key()
            
        Returns:
            Dict matching AI output structure:
            {
                "budget_variances": {
                    "Revenue": {"Metric Name": ["Q1", "Q2"]},
                    ...
                },
                "trailing_anomalies": {...}
            }
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT section, category, metric, questions
            FROM question_overrides
            WHERE property_key = ?
        """, (property_key,))
        
        result = {
            "budget_variances": {"Revenue": {}, "Expenses": {}, "Balance Sheet": {}},
            "trailing_anomalies": {"Revenue": {}, "Expenses": {}, "Balance Sheet": {}}
        }
        
        for row in cursor.fetchall():
            section = row["section"]
            category = row["category"]
            metric = row["metric"]
            questions = json.loads(row["questions"])
            
            if section in result and category in result[section]:
                result[section][category][metric] = questions
        
        return result
    
    def save_override(
        self, 
        property_key: str, 
        section: str, 
        category: str, 
        metric: str, 
        questions: List[str]
    ) -> bool:
        """
        Save or update a single metric's questions.
        
        Args:
            property_key: Key from make_key()
            section: "budget_variances" or "trailing_anomalies"
            category: "Revenue", "Expenses", or "Balance Sheet"
            metric: Metric name
            questions: List of question strings
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO question_overrides (property_key, section, category, metric, questions, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(property_key, section, category, metric) 
                DO UPDATE SET questions = excluded.questions, updated_at = excluded.updated_at
            """, (property_key, section, category, metric, json.dumps(questions), datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Saved override for {property_key}/{section}/{category}/{metric}")
            return True
        except Exception as e:
            logger.error(f"Error saving override: {e}")
            return False
    
    def save_bulk_overrides(
        self, 
        property_key: str, 
        section: str, 
        overrides: Dict[str, Dict[str, List[str]]]
    ) -> bool:
        """
        Save multiple metric overrides for a section.
        
        Args:
            property_key: Key from make_key()
            section: "budget_variances" or "trailing_anomalies"
            overrides: {category: {metric: [questions]}}
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            for category, metrics in overrides.items():
                for metric, questions in metrics.items():
                    cursor.execute("""
                        INSERT INTO question_overrides (property_key, section, category, metric, questions, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(property_key, section, category, metric) 
                        DO UPDATE SET questions = excluded.questions, updated_at = excluded.updated_at
                    """, (property_key, section, category, metric, json.dumps(questions), datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Bulk saved overrides for {property_key}/{section}")
            return True
        except Exception as e:
            logger.error(f"Error in bulk save: {e}")
            return False
    
    def has_overrides(self, property_key: str) -> bool:
        """
        Check if any overrides exist for a property/period.
        
        Args:
            property_key: Key from make_key()
            
        Returns:
            True if overrides exist
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM question_overrides WHERE property_key = ?
        """, (property_key,))
        row = cursor.fetchone()
        return row["cnt"] > 0 if row else False
    
    def delete_overrides(self, property_key: str) -> bool:
        """
        Delete all overrides for a property/period.
        
        Args:
            property_key: Key from make_key()
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM question_overrides WHERE property_key = ?
            """, (property_key,))
            self.conn.commit()
            logger.info(f"Deleted overrides for {property_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting overrides: {e}")
            return False

    def has_analysis(self, property_key: str) -> bool:
        """Check if a previous analysis exists."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM last_analysis WHERE property_key = ?", (property_key,))
        row = cursor.fetchone()
        return row["cnt"] > 0 if row else False

    def save_analysis(self, property_key: str, analysis_data: Dict[str, Any]) -> bool:
        """Save a full analysis result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO last_analysis (property_key, analysis_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(property_key) DO UPDATE SET 
                analysis_json = excluded.analysis_json, 
                updated_at = excluded.updated_at
            """, (property_key, json.dumps(analysis_data, default=str), datetime.now().isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False

    def get_analysis(self, property_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a previous analysis result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT analysis_json FROM last_analysis WHERE property_key = ?", (property_key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["analysis_json"])
            return None
        except Exception as e:
            logger.error(f"Error getting analysis: {e}")
            return None

    def delete_analysis(self, property_key: str) -> bool:
        """Delete saved analysis."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM last_analysis WHERE property_key = ?", (property_key,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


# Global instance for easy access
question_store = QuestionStore()
