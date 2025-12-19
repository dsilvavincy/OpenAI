"""
Local Property Analysis Module
Performs all Python analytics on property data before sending to LLM.
Replaces code_interpreter functionality from Assistants API.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PropertyAnalyzer:
    """
    Performs comprehensive property analysis on monthly and YTD dataframes.
    Outputs structured JSON data ready for Responses API.
    """
    
    # Key metrics that should always be present
    KEY_METRICS = [
        'Property Asking Rent',
        'Loss to lease',
        'Gross Scheduled Rent',
        'Vacancy',
        'Non Revenue Units',
        'Concessions',
        'Delinquency',
        'Effective Rental Income',
        'Net Eff. Gross Income',
        'Total Expense',
        'EBITDA (NOI)',
        'Monthly Cash Flow',
        'Debt Service',
    ]
    
    # Metrics to track for MoM changes
    MOM_METRICS = [
        'Net Eff. Gross Income',
        'Total Expense',
        'EBITDA (NOI)',
        'Delinquency',
        'Vacancy',
        'Effective Rental Income',
    ]
    
    # Industry benchmarks - provided to LLM for reference, NOT for hardcoded rules
    # The LLM will use these as context to generate its own reasoning and questions
    INDUSTRY_BENCHMARKS = {
        'typical_vacancy_rate': 5.0,  # % - typical for stabilized properties
        'high_vacancy_rate': 10.0,  # % - concerning level
        'typical_delinquency_rate': 2.0,  # % - typical collection loss
        'high_delinquency_rate': 5.0,  # % - concerning level
        'typical_expense_ratio': 45.0,  # % - typical for multifamily
        'high_expense_ratio': 55.0,  # % - concerning level
    }
    
    def __init__(self, monthly_df: pd.DataFrame, ytd_df: pd.DataFrame):
        """
        Initialize with monthly and YTD dataframes.
        
        Args:
            monthly_df: DataFrame with monthly property data (filtered from preprocessing)
            ytd_df: DataFrame with YTD cumulative data
        """
        self.monthly_df = monthly_df.copy()
        self.ytd_df = ytd_df.copy()
        
        # Ensure MonthParsed is datetime
        if 'MonthParsed' in self.monthly_df.columns:
            self.monthly_df['MonthParsed'] = pd.to_datetime(self.monthly_df['MonthParsed'])
        if 'MonthParsed' in self.ytd_df.columns:
            self.ytd_df['MonthParsed'] = pd.to_datetime(self.ytd_df['MonthParsed'])
    
    def get_available_properties(self) -> List[str]:
        """Get list of unique properties in the data."""
        properties = []
        
        # Check for Property column (may be empty for single-property files)
        if 'Property' in self.monthly_df.columns:
            properties = self.monthly_df['Property'].dropna().unique().tolist()
        
        # Also check Sheet column for property names
        if 'Sheet' in self.monthly_df.columns and not properties:
            properties = self.monthly_df['Sheet'].dropna().unique().tolist()
        
        return sorted(set(properties))
    
    def analyze_property(self, property_name: str) -> Dict[str, Any]:
        """
        Complete analysis for a single property.
        
        Args:
            property_name: Name of property to analyze
            
        Returns:
            Dict with all computed metrics ready for LLM
        """
        # Filter data to this property
        monthly_filtered = self._filter_by_property(self.monthly_df, property_name)
        ytd_filtered = self._filter_by_property(self.ytd_df, property_name)
        
        # Get time periods
        latest_month = self._get_latest_month(monthly_filtered)
        prior_month = self._get_prior_month(monthly_filtered, latest_month)
        
        # Build the structured output
        result = {
            "property_name": property_name,
            "report_period": latest_month.strftime("%B %Y") if latest_month else "Unknown",
            "prior_period": prior_month.strftime("%B %Y") if prior_month else "N/A",
            "generated_at": datetime.now().isoformat(),
            
            # Industry benchmarks for LLM to use in reasoning
            "industry_benchmarks": self.INDUSTRY_BENCHMARKS,
            
            "validation": self._get_validation_info(monthly_filtered, ytd_filtered, property_name),
            "current_month": self._get_period_metrics(monthly_filtered, latest_month),
            "prior_month": self._get_period_metrics(monthly_filtered, prior_month) if prior_month else {},
            "mom_changes": self._calculate_mom_changes(monthly_filtered, latest_month, prior_month),
            "t12_trends": self._get_t12_trends(monthly_filtered),
            "ytd_cumulative": self._get_ytd_performance(ytd_filtered),
            "key_ratios": self._calculate_key_ratios(monthly_filtered, ytd_filtered, latest_month),
            "budget_variance": self._get_budget_variance(monthly_filtered, ytd_filtered, latest_month),
            "rolling_avg_variance": self._get_rolling_average_variances(monthly_filtered, latest_month),
            # Data highlights - LLM will interpret these and generate red flags/questions
            "data_highlights": self._get_data_highlights(monthly_filtered, ytd_filtered, latest_month),
            "all_metrics_current": self._get_all_metrics_for_period(monthly_filtered, latest_month),
            "monthly_time_series": self._get_monthly_time_series(monthly_filtered),
            "debug": {
                "detected_latest_month": latest_month.strftime("%Y-%m-%d") if latest_month else None,
                "detection_reason": getattr(self, "_last_detection_reason", "Fallback to absolute max")
            }
        }
        
        # Sanitize for JSON (convert NaN/Inf to None)
        return self._sanitize_for_json(result)

    def _sanitize_for_json(self, data: Any) -> Any:
        """Recursively convert NaN and Inf to None for valid JSON."""
        if isinstance(data, dict):
            return {k: self._sanitize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_for_json(v) for v in data]
        elif isinstance(data, float):
            if np.isnan(data) or np.isinf(data):
                return None
            return data
        return data
    
    def _filter_by_property(self, df: pd.DataFrame, property_name: str) -> pd.DataFrame:
        """Filter DataFrame to specific property."""
        if df.empty:
            return df
        
        # Try Property column first
        if 'Property' in df.columns:
            # Handle both exact match and partial match
            mask = (df['Property'] == property_name) | (df['Property'].fillna('').str.contains(property_name, case=False, na=False))
            filtered = df[mask]
            if not filtered.empty:
                return filtered
        
        # Try Sheet column
        if 'Sheet' in df.columns:
            mask = df['Sheet'].str.contains(property_name, case=False, na=False)
            filtered = df[mask]
            if not filtered.empty:
                return filtered
        
        # If no match found, return empty DataFrame with same structure
        logger.warning(f"No data found for property: {property_name}")
        return df.iloc[0:0]
    
    def _get_latest_month(self, df: pd.DataFrame) -> Optional[datetime]:
        """Find the latest month in the data that actually has values."""
        if df.empty or 'MonthParsed' not in df.columns:
            return None
            
        # Ensure Value is numeric for the check
        check_df = df.copy()
        check_df['ValueNumeric'] = pd.to_numeric(check_df['Value'], errors='coerce')
        
        # We specifically look for key metrics that define "active" months (Income/Expense/NOI)
        active_metrics = ['Net Eff. Gross Income', 'Total Expense', 'EBITDA (NOI)']
        data_mask = (check_df['ValueNumeric'].notna()) & (check_df['ValueNumeric'] != 0)
        
        # More robust matching (strip and lower)
        metric_mask = check_df['Metric'].fillna('').str.strip().str.lower().isin([m.lower() for m in active_metrics])
        
        active_data = check_df[data_mask & metric_mask]
        
        if not active_data.empty:
            latest = active_data['MonthParsed'].max()
            self._last_detection_reason = f"Found data for core metrics up to {latest.strftime('%B %Y')}"
            return latest
            
        # Second attempt: Look for ANY metric with data
        any_data = check_df[data_mask]
        if not any_data.empty:
            latest = any_data['MonthParsed'].max()
            self._last_detection_reason = f"No core metrics, found other data up to {latest.strftime('%B %Y')}"
            return latest
            
        # Fallback to absolute max if no data found at all
        self._last_detection_reason = "No actual values found; falling back to absolute calendar maximum"
        return df['MonthParsed'].max()
    
    def _get_prior_month(self, df: pd.DataFrame, latest_month: Optional[datetime]) -> Optional[datetime]:
        """Find the month before the latest."""
        if df.empty or latest_month is None or 'MonthParsed' not in df.columns:
            return None
        
        prior_months = df[df['MonthParsed'] < latest_month]['MonthParsed'].unique()
        if len(prior_months) == 0:
            return None
        return pd.Timestamp(max(prior_months))
    
    def _get_validation_info(self, monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, property_name: str) -> Dict:
        """Get validation information about the data."""
        return {
            "property_selected": property_name,
            "monthly_rows": len(monthly_df),
            "ytd_rows": len(ytd_df),
            "months_available": sorted(monthly_df['MonthParsed'].dt.strftime('%Y-%m').unique().tolist()) if not monthly_df.empty else [],
            "metrics_count": monthly_df['Metric'].nunique() if not monthly_df.empty else 0,
        }
    
    def _get_metric_value(self, df: pd.DataFrame, metric_name: str, month: Optional[datetime] = None) -> Optional[float]:
        """Get value for a specific metric, optionally for a specific month."""
        if df.empty:
            return None
        
        filtered = df[df['Metric'].str.lower() == metric_name.lower()]
        
        if month is not None and 'MonthParsed' in df.columns:
            filtered = filtered[filtered['MonthParsed'] == month]
        
        if filtered.empty:
            # Try partial match
            filtered = df[df['Metric'].str.contains(metric_name, case=False, na=False)]
            if month is not None and 'MonthParsed' in df.columns:
                filtered = filtered[filtered['MonthParsed'] == month]
        
        if not filtered.empty:
            return float(filtered['Value'].iloc[0])
        return None
    
    def _get_period_metrics(self, df: pd.DataFrame, month: Optional[datetime]) -> Dict:
        """Get all key metrics for a specific month (including budgets if available)."""
        if month is None:
            return {}
        
        metrics = {}
        for metric in self.KEY_METRICS:
            # Find value and budget
            vals = self._get_metric_values(df, metric, month)
            if vals["value"] is not None:
                key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
                metrics[key] = round(vals["value"], 2)
                if vals["budget"] is not None:
                    metrics[f"{key}_budget"] = round(vals["budget"], 2)
                    # Calculate variance if both exist
                    variance_abs = vals["value"] - vals["budget"]
                    metrics[f"{key}_variance_abs"] = round(variance_abs, 2)
                    if vals["budget"] != 0:
                        metrics[f"{key}_variance_pct"] = round((variance_abs / abs(vals["budget"])) * 100, 2)
        
        return metrics

    def _get_metric_values(self, df: pd.DataFrame, metric_name: str, month: Optional[datetime] = None) -> Dict[str, Optional[float]]:
        """Get both actual and budget value for a metric."""
        if df.empty:
            return {"value": None, "budget": None}
        
        # Exact match
        filtered = df[df['Metric'].str.lower() == metric_name.lower()]
        if (month_filtered := self._apply_month_filter(filtered, month)) is not None:
            filtered = month_filtered
        
        # Partial match if exact failed
        if filtered.empty:
            filtered = df[df['Metric'].str.contains(metric_name, case=False, na=False)]
            if (month_filtered := self._apply_month_filter(filtered, month)) is not None:
                filtered = month_filtered
        
        if not filtered.empty:
            row = filtered.iloc[0]
            val = float(row['Value']) if pd.notna(row['Value']) else None
            budget = float(row['BudgetValue']) if 'BudgetValue' in row and pd.notna(row['BudgetValue']) else None
            return {"value": val, "budget": budget}
            
        return {"value": None, "budget": None}

    def _apply_month_filter(self, df: pd.DataFrame, month: Optional[datetime]) -> Optional[pd.DataFrame]:
        """Utility to apply month filter if applicable."""
        if month is not None and 'MonthParsed' in df.columns:
            m_filtered = df[df['MonthParsed'] == month]
            if not m_filtered.empty:
                return m_filtered
        return None
    
    def _get_all_metrics_for_period(self, df: pd.DataFrame, month: Optional[datetime]) -> Dict:
        """Get ALL metrics for a specific month (including budgets)."""
        if month is None or df.empty:
            return {}
        
        month_data = df[df['MonthParsed'] == month]
        metrics = {}
        
        for _, row in month_data.iterrows():
            metric_name = row['Metric']
            value = row['Value']
            budget = row.get('BudgetValue') if 'BudgetValue' in row else None
            
            if pd.notna(value) or pd.notna(budget):
                metrics[metric_name] = {
                    "actual": round(float(value), 2) if pd.notna(value) else None,
                    "budget": round(float(budget), 2) if pd.notna(budget) else None
                }
        
        return metrics
    
    def _calculate_mom_changes(self, df: pd.DataFrame, current_month: Optional[datetime], prior_month: Optional[datetime]) -> Dict:
        """Calculate month-over-month changes for key metrics."""
        if current_month is None or prior_month is None:
            return {"note": "Insufficient data for MoM comparison"}
        
        changes = {}
        
        for metric in self.MOM_METRICS:
            current_val = self._get_metric_value(df, metric, current_month)
            prior_val = self._get_metric_value(df, metric, prior_month)
            
            if current_val is not None and prior_val is not None:
                key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
                
                abs_change = current_val - prior_val
                pct_change = ((current_val - prior_val) / abs(prior_val) * 100) if prior_val != 0 else 0
                
                changes[key] = {
                    "current": round(current_val, 2),
                    "prior": round(prior_val, 2),
                    "change_abs": round(abs_change, 2),
                    "change_pct": round(pct_change, 2),
                }
        
        return changes
    
    def _get_ytd_performance(self, ytd_df: pd.DataFrame) -> Dict:
        """Get YTD cumulative performance metrics (including budgets)."""
        if ytd_df.empty:
            return {"note": "No YTD data available"}
        
        ytd_metrics = {}
        
        # Key YTD metrics
        ytd_keys = [
            'Net Eff. Gross Income',
            'Total Expense',
            'EBITDA (NOI)',
            'Property Asking Rent',
            'Effective Rental Income',
            'Monthly Cash Flow',
        ]
        
        for metric in ytd_keys:
            vals = self._get_metric_values(ytd_df, metric)
            if vals["value"] is not None:
                key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
                ytd_metrics[key] = round(vals["value"], 2)
                if vals["budget"] is not None:
                    ytd_metrics[f"{key}_budget"] = round(vals["budget"], 2)
                    variance_abs = vals["value"] - vals["budget"]
                    ytd_metrics[f"{key}_variance_abs"] = round(variance_abs, 2)
                    if vals["budget"] != 0:
                        ytd_metrics[f"{key}_variance_pct"] = round((variance_abs / abs(vals["budget"])) * 100, 2)
        
        # Calculate YTD expense ratio
        income = self._get_metric_value(ytd_df, 'Net Eff. Gross Income')
        expenses = self._get_metric_value(ytd_df, 'Total Expense')
        
        if income and expenses and income != 0:
            ytd_metrics['expense_ratio_pct'] = round(abs(expenses) / income * 100, 2)
        
        return ytd_metrics

    def _get_budget_variance(self, monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, month: Optional[datetime]) -> Dict:
        """Specifically extract budget variances for detailed analysis."""
        if 'BudgetValue' not in monthly_df.columns:
            return {"note": "Budget data not available in this format"}
            
        variances = {
            "monthly": {},
            "ytd": {}
        }
        
        # Expanded check metrics to include more detail if available
        check_metrics = ['Net Eff. Gross Income', 'Total Expense', 'EBITDA (NOI)', 'Property Asking Rent', 'Effective Rental Income']
        
        for metric in check_metrics:
            key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
            
            # Monthly
            m_vals = self._get_metric_values(monthly_df, metric, month)
            if m_vals["value"] is not None and m_vals["budget"] is not None:
                var_abs = m_vals["value"] - m_vals["budget"]
                variances["monthly"][key] = {
                    "actual": round(m_vals["value"], 2),
                    "budget": round(m_vals["budget"], 2),
                    "variance_abs": round(var_abs, 2),
                    "variance_pct": round((var_abs / abs(m_vals["budget"])) * 100, 2) if m_vals["budget"] != 0 else 0
                }
            
            # YTD
            y_vals = self._get_metric_values(ytd_df, metric)
            if y_vals["value"] is not None and y_vals["budget"] is not None:
                var_abs = y_vals["value"] - y_vals["budget"]
                variances["ytd"][key] = {
                    "actual": round(y_vals["value"], 2),
                    "budget": round(y_vals["budget"], 2),
                    "variance_abs": round(var_abs, 2),
                    "variance_pct": round((var_abs / abs(y_vals["budget"])) * 100, 2) if y_vals["budget"] != 0 else 0
                }
        
        return variances

    def _get_rolling_average_variances(self, df: pd.DataFrame, current_month: Optional[datetime]) -> Dict:
        """Calculate variance between current month and prior 3-month average."""
        if current_month is None or df.empty:
            return {}
            
        variances = {}
        metrics_to_check = ['Total Expense', 'Net Eff. Gross Income', 'EBITDA (NOI)', 'Property Asking Rent']
        
        for metric in metrics_to_check:
            metric_data = df[df['Metric'].str.lower() == metric.lower()].sort_values('MonthParsed')
            if metric_data.empty:
                continue
                
            # Filter to months before current
            prior_data = metric_data[metric_data['MonthParsed'] < current_month].tail(3)
            current_row = metric_data[metric_data['MonthParsed'] == current_month]
            
            if not prior_data.empty and not current_row.empty:
                # Filter out NaN/Zero from prior data for a more meaningful average
                valid_priors = prior_data['Value'][prior_data['Value'].notna() & (prior_data['Value'] != 0)]
                if valid_priors.empty:
                    continue
                    
                avg_3mo = valid_priors.mean()
                current_val = current_row['Value'].iloc[0]
                
                if pd.isna(current_val) or pd.isna(avg_3mo):
                    continue
                
                key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
                var_abs = current_val - avg_3mo
                var_pct = (var_abs / abs(avg_3mo) * 100) if avg_3mo != 0 else 0
                
                variances[key] = {
                    "current": round(float(current_val), 2),
                    "prior_3mo_avg": round(float(avg_3mo), 2),
                    "variance_abs": round(float(var_abs), 2),
                    "variance_pct": round(float(var_pct), 2)
                }
                
        return variances
    
    def _calculate_key_ratios(self, monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, month: Optional[datetime]) -> Dict:
        """Calculate key performance ratios."""
        if month is None:
            return {}
        
        ratios = {}
        
        # Get values for calculations
        asking_rent = self._get_metric_value(monthly_df, 'Property Asking Rent', month)
        effective_income = self._get_metric_value(monthly_df, 'Net Eff. Gross Income', month)
        gross_rent = self._get_metric_value(monthly_df, 'Gross Scheduled Rent', month)
        vacancy = self._get_metric_value(monthly_df, 'Vacancy', month)
        delinquency = self._get_metric_value(monthly_df, 'Delinquency', month)
        total_expense = self._get_metric_value(monthly_df, 'Total Expense', month)
        loss_to_lease = self._get_metric_value(monthly_df, 'Loss to lease', month)
        
        # Collection Rate
        if asking_rent and effective_income and asking_rent != 0:
            ratios['collection_rate_pct'] = round(effective_income / asking_rent * 100, 2)
        
        # Vacancy Rate
        if asking_rent and vacancy and asking_rent != 0:
            ratios['vacancy_rate_pct'] = round(abs(vacancy) / asking_rent * 100, 2)
        
        # Delinquency Rate
        if effective_income and delinquency:
            ratios['delinquency_rate_pct'] = round(abs(delinquency) / abs(effective_income) * 100, 2) if effective_income != 0 else 0
        
        # Expense Ratio (monthly)
        if effective_income and total_expense:
            ratios['expense_ratio_pct'] = round(abs(total_expense) / effective_income * 100, 2) if effective_income != 0 else 0
        
        # Loss-to-Lease Rate
        if asking_rent and loss_to_lease and asking_rent != 0:
            ratios['loss_to_lease_rate_pct'] = round(abs(loss_to_lease) / asking_rent * 100, 2)
        
        # Economic Occupancy
        if gross_rent and effective_income and gross_rent != 0:
            ratios['economic_occupancy_pct'] = round(effective_income / gross_rent * 100, 2)
        
        return ratios
    
    def _get_data_highlights(self, monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, month: Optional[datetime]) -> Dict[str, Any]:
        """
        Get notable data points for LLM to interpret.
        This provides FACTUAL OBSERVATIONS only - the LLM generates the reasoning,
        questions, red flags, and recommendations.
        """
        if month is None:
            return {"note": "No data available for analysis"}
        
        highlights = {}
        
        # Get key values for the current month
        asking_rent = self._get_metric_value(monthly_df, 'Property Asking Rent', month)
        vacancy = self._get_metric_value(monthly_df, 'Vacancy', month)
        delinquency = self._get_metric_value(monthly_df, 'Delinquency', month)
        effective_income = self._get_metric_value(monthly_df, 'Net Eff. Gross Income', month)
        total_expense = self._get_metric_value(monthly_df, 'Total Expense', month)
        noi = self._get_metric_value(monthly_df, 'EBITDA (NOI)', month)
        
        # Key rates (factual, no judgments)
        if asking_rent and asking_rent != 0:
            if vacancy:
                highlights['vacancy_rate_pct'] = round(abs(vacancy) / asking_rent * 100, 2)
        
        if effective_income and effective_income != 0:
            if delinquency:
                highlights['delinquency_rate_pct'] = round(abs(delinquency) / abs(effective_income) * 100, 2)
            if total_expense:
                highlights['expense_ratio_pct'] = round(abs(total_expense) / effective_income * 100, 2)
        
        # Budget Variances (Factual)
        if 'budget_variance' in highlights is False: # Check if we need to add it
             # We can pull from the already computed budget_variance section if we want, 
             # but here we'll add specific high-level flags
             m_vars = self._get_budget_variance(monthly_df, ytd_df, month)
             if "note" not in m_vars:
                 if noi_var := m_vars["monthly"].get("ebitda_noi"):
                     highlights["monthly_noi_variance_pct"] = noi_var["variance_pct"]
                 if ytd_noi_var := m_vars["ytd"].get("ebitda_noi"):
                     highlights["ytd_noi_variance_pct"] = ytd_noi_var["variance_pct"]

        # MoM changes with largest movements (factual)
        prior_month = self._get_prior_month(monthly_df, month)
        if prior_month:
            significant_changes = []
            for metric in self.MOM_METRICS:
                current_val = self._get_metric_value(monthly_df, metric, month)
                prior_val = self._get_metric_value(monthly_df, metric, prior_month)
                
                if current_val is not None and prior_val is not None and prior_val != 0:
                    pct_change = ((current_val - prior_val) / abs(prior_val)) * 100
                    significant_changes.append({
                        "metric": metric,
                        "current": round(current_val, 2),
                        "prior": round(prior_val, 2),
                        "change_pct": round(pct_change, 2),
                        "abs_change": round(current_val - prior_val, 2),
                    })
            
            # Sort by absolute change magnitude
            significant_changes.sort(key=lambda x: abs(x['change_pct']), reverse=True)
            highlights['largest_mom_changes'] = significant_changes[:5]  # Top 5 changes
        
        # Zero values that might indicate missing data or issues
        zero_metrics = []
        for metric in self.KEY_METRICS:
            val = self._get_metric_value(monthly_df, metric, month)
            if val is not None and val == 0:
                zero_metrics.append(metric)
        if zero_metrics:
            highlights['zero_value_metrics'] = zero_metrics
        
        # Count of months with actual data (non-zero)
        data_months = monthly_df[monthly_df['Value'] != 0]['MonthParsed'].nunique() if not monthly_df.empty else 0
        highlights['months_with_data'] = data_months
        
        return highlights
    
    def _get_t12_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate trailing 12-month trends for key metrics.
        This is the core T12 analysis that considers all months of data.
        """
        if df.empty or 'MonthParsed' not in df.columns:
            return {"note": "Insufficient data for T12 analysis"}
        
        trends = {}
        
        # Metrics to analyze for T12 trends
        trend_metrics = [
            'Net Eff. Gross Income',
            'Total Expense',
            'EBITDA (NOI)',
            'Effective Rental Income',
            'Vacancy',
            'Delinquency',
            'Property Asking Rent',
        ]
        
        for metric in trend_metrics:
            metric_data = df[df['Metric'].str.lower() == metric.lower()].copy()
            
            if metric_data.empty:
                # Try partial match
                metric_data = df[df['Metric'].str.contains(metric, case=False, na=False)].copy()
            
            if metric_data.empty:
                continue
            
            # Sort by month
            metric_data = metric_data.sort_values('MonthParsed')
            values = metric_data['Value'].dropna().tolist()
            months = metric_data['MonthParsed'].tolist()
            
            if len(values) < 2:
                continue
            
            key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
            
            # Calculate T12 statistics
            t12_stats = {
                "months_of_data": len(values),
                "t12_average": round(float(np.mean(values)), 2),
                "t12_total": round(float(np.sum(values)), 2),
                "t12_min": round(float(np.min(values)), 2),
                "t12_min_month": min(months).strftime("%B %Y") if months else None,
                "t12_max": round(float(np.max(values)), 2),
                "t12_max_month": max(months).strftime("%B %Y") if months else None,
                "t12_std_dev": round(float(np.std(values)), 2),
            }
            
            # Calculate 3-month rolling average (if enough data)
            if len(values) >= 3:
                t12_stats["rolling_3mo_avg"] = round(float(np.mean(values[-3:])), 2)
            
            # Calculate 6-month rolling average (if enough data)
            if len(values) >= 6:
                t12_stats["rolling_6mo_avg"] = round(float(np.mean(values[-6:])), 2)
            
            # Calculate overall trend direction and magnitude
            if len(values) >= 3:
                first_half_avg = np.mean(values[:len(values)//2])
                second_half_avg = np.mean(values[len(values)//2:])
                
                if first_half_avg != 0:
                    trend_pct = ((second_half_avg - first_half_avg) / abs(first_half_avg)) * 100
                    t12_stats["trend_direction"] = "increasing" if trend_pct > 5 else ("decreasing" if trend_pct < -5 else "stable")
                    t12_stats["trend_magnitude_pct"] = round(trend_pct, 2)
                else:
                    t12_stats["trend_direction"] = "unknown"
                    t12_stats["trend_magnitude_pct"] = 0
                    
            # Calculate first month vs last month change
            first_val = values[0]
            last_val = values[-1]
            if first_val != 0:
                total_change_pct = ((last_val - first_val) / abs(first_val)) * 100
                t12_stats["period_start_value"] = round(first_val, 2)
                t12_stats["period_end_value"] = round(last_val, 2)
                t12_stats["total_change_pct"] = round(total_change_pct, 2)
            
            trends[key] = t12_stats
        
        return trends
    
    def _get_monthly_time_series(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Get complete monthly time series for key metrics.
        Provides the full 12 months of data for each metric.
        """
        if df.empty or 'MonthParsed' not in df.columns:
            return {}
        
        time_series = {}
        
        # Get all unique months sorted
        all_months = sorted(df['MonthParsed'].unique())
        
        # Key metrics to include in time series
        series_metrics = [
            'Net Eff. Gross Income',
            'Total Expense',
            'EBITDA (NOI)',
            'Vacancy',
            'Delinquency',
            'Property Asking Rent',
            'Effective Rental Income',
        ]
        
        for metric in series_metrics:
            metric_data = df[df['Metric'].str.lower() == metric.lower()].copy()
            
            if metric_data.empty:
                metric_data = df[df['Metric'].str.contains(metric, case=False, na=False)].copy()
            
            if metric_data.empty:
                continue
            
            key = metric.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('.', '')
            
            # Build time series list
            series = []
            metric_data = metric_data.sort_values('MonthParsed')
            
            for _, row in metric_data.iterrows():
                series.append({
                    "month": row['MonthParsed'].strftime("%Y-%m"),
                    "month_name": row['MonthParsed'].strftime("%B %Y"),
                    "value": round(float(row['Value']), 2) if pd.notna(row['Value']) else None
                })
            
            time_series[key] = series
        
        return time_series


def prepare_analysis_for_llm(monthly_df: pd.DataFrame, ytd_df: pd.DataFrame, property_name: str) -> Dict[str, Any]:
    """
    Convenience function to prepare analysis data for Responses API.
    
    Args:
        monthly_df: Monthly property data
        ytd_df: YTD cumulative data
        property_name: Property to analyze
        
    Returns:
        Structured dict ready to send to LLM
    """
    analyzer = PropertyAnalyzer(monthly_df, ytd_df)
    return analyzer.analyze_property(property_name)
