"""
T12 Monthly Financial KPI Calculator

Handles KPI calculations specific to T12 monthly property financial data.
Refactored from the original KPI summary logic to fit the plugin architecture.
"""
import pandas as pd
from typing import List, Dict
from .base_kpi_calculator import BaseKPICalculator

class T12MonthlyFinancialKPICalculator(BaseKPICalculator):
    """
    KPI Calculator for T12 Monthly Financial format.
    
    Calculates:
    - Revenue performance metrics
    - Expense analysis
    - NOI and below-line items
    - Trend analysis (month-over-month)
    - Key performance ratios
    - YTD summaries
    """
    
    def __init__(self):
        super().__init__(
            format_name="T12_Monthly_Financial",
            calculator_description="KPI Calculator for T12 Monthly Property Financial Reports"
        )
    
    def calculate_kpis(self, df: pd.DataFrame) -> str:
        """
        Calculate comprehensive KPI summary for T12 data.
        
        Args:
            df: Processed T12 DataFrame
            
        Returns:
            str: Formatted KPI summary for AI analysis
        """
        try:
            self.clear_calculation_issues()
            
            if not self.validate_data_structure(df):
                return "Error: Invalid data structure for KPI calculation"
            
            summary_parts = []
            
            # Get latest month data for current performance
            latest_data = self.get_latest_period_data(df)
            if latest_data.empty:
                return "No monthly data found to analyze."
            
            # Get the latest month name for header
            if 'MonthParsed' in latest_data.columns:
                latest_month = latest_data["MonthParsed"].max()
                month_str = latest_month.strftime('%B %Y')
            elif 'PeriodParsed' in latest_data.columns:
                latest_month = latest_data["PeriodParsed"].max()
                month_str = latest_month.strftime('%B %Y')
            else:
                month_str = "Latest Period"
            
            # Header
            summary_parts.append(f"=== T12 PROPERTY ANALYSIS - {month_str} ===")
            summary_parts.append(f"Sheet: {df['Sheet'].iloc[0]}")
            summary_parts.append("")
            
            # Group metrics by categories for latest month
            grouped_metrics = self.group_metrics_by_category(latest_data)
            
            # Display each category
            category_titles = {
                "REVENUE_PERFORMANCE": "=== REVENUE PERFORMANCE ===",
                "REVENUE_LOSS_FACTORS": "=== REVENUE LOSS FACTORS ===", 
                "EXPENSES": "=== EXPENSES ===",
                "NOI_AND_BELOW_LINE": "=== NOI & BELOW LINE ===",
                "BALANCE_SHEET_ESCROW": "=== BALANCE SHEET & ESCROW ===",
                "OTHER_METRICS": "=== OTHER METRICS ==="
            }
            
            for category, title in category_titles.items():
                if category in grouped_metrics:
                    summary_parts.append(title)
                    summary_parts.extend(grouped_metrics[category])
                    summary_parts.append("")
            
            # Add trend analysis
            trends = self.calculate_trends(df)
            if trends:
                summary_parts.append("=== MONTH-OVER-MONTH TRENDS ===")
                summary_parts.extend(trends)
                summary_parts.append("")
            
            # Add ratio analysis
            ratios = self.calculate_ratios(latest_data)
            if ratios:
                summary_parts.append("=== KEY PERFORMANCE RATIOS ===")
                summary_parts.extend(ratios)
                summary_parts.append("")
            
            # Add YTD summary if available
            ytd_summary = self._generate_ytd_summary(df)
            if ytd_summary:
                summary_parts.extend(ytd_summary)
            
            # Log any calculation issues
            self.log_calculation_issues()
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.add_calculation_issue(f"Error in KPI calculation: {str(e)}")
            return f"Error generating T12 KPI summary: {str(e)}"
    
    def get_key_metrics(self) -> List[str]:
        """
        Get list of key T12 metrics this calculator focuses on.
        
        Returns:
            List[str]: Key T12 metric names
        """
        return [
            "Property Asking Rent",
            "Effective Rental Income",
            "Gross Scheduled Rent", 
            "Loss to lease",
            "Vacancy",
            "Concessions",
            "Delinquency",
            "EBITDA (NOI)",
            "Total Expense",
            "Management Fee",
            "Property Taxes",
            "Insurance",
            "Monthly Cash Flow"
        ]
    
    def calculate_trends(self, df: pd.DataFrame) -> List[str]:
        """
        Calculate month-over-month trends for key T12 metrics.
        
        Args:
            df: Processed T12 DataFrame
            
        Returns:
            List[str]: List of trend analysis strings
        """
        trends = []
        
        # Only analyze non-YTD monthly data
        monthly_data = df[~df["IsYTD"]].copy()
        if monthly_data.empty:
            return trends
        
        key_metrics = [
            'Effective Rental Income', 
            'Property Asking Rent', 
            'Vacancy', 
            'Delinquency', 
            'Loss to lease',
            'EBITDA',
            'NOI',
            'Total Expense'
        ]
        
        for metric in key_metrics:
            try:
                # Get data for this metric across all months
                metric_data = monthly_data[
                    monthly_data['Metric'].str.contains(metric, case=False, na=False)
                ].copy()
                
                if len(metric_data) >= 2:
                    # Sort by period and calculate change
                    if 'MonthParsed' in metric_data.columns:
                        metric_data = metric_data.sort_values('MonthParsed')
                    elif 'PeriodParsed' in metric_data.columns:
                        metric_data = metric_data.sort_values('PeriodParsed')
                    elif 'Month' in metric_data.columns:
                        metric_data = metric_data.sort_values('Month')
                    else:
                        # No valid time column found, skip this metric
                        self.add_calculation_issue(f"Error calculating trend for {metric}: No valid time column found")
                        continue
                    
                    values = metric_data['Value'].tolist()
                    
                    if len(values) >= 2:
                        latest = values[-1]
                        previous = values[-2]
                        change = latest - previous
                        pct_change = (change / abs(previous)) * 100 if previous != 0 else 0
                        
                        direction = "increased" if change > 0 else "decreased"
                        change_str = self.format_currency(abs(change))
                        pct_str = f"{abs(pct_change):.1f}%"
                        
                        trends.append(f"• {metric}: {direction} by {change_str} ({pct_str})")
                        
            except Exception as e:
                self.add_calculation_issue(f"Error calculating trend for {metric}: {str(e)}")
                continue
        
        return trends
    
    def calculate_ratios(self, latest_data: pd.DataFrame) -> List[str]:
        """
        Calculate key performance ratios for T12 data.
        
        Args:
            latest_data: DataFrame with latest period data
            
        Returns:
            List[str]: List of ratio calculation strings
        """
        ratios = []
        
        try:
            # Get key values for ratio calculations
            asking_rent = self.get_metric_value(latest_data, 'Property Asking Rent')
            effective_income = self.get_metric_value(latest_data, 'Effective Rental Income')
            gross_rent = self.get_metric_value(latest_data, 'Gross Scheduled Rent')
            loss_to_lease = self.get_metric_value(latest_data, 'Loss to lease')
            vacancy = self.get_metric_value(latest_data, 'Vacancy')
            total_expense = self.get_metric_value(latest_data, 'Total Expense')
            noi = self.get_metric_value(latest_data, 'EBITDA (NOI)')
            
            # Collection Rate (Effective Income / Asking Rent)
            if asking_rent and effective_income and asking_rent > 0:
                collection_rate = (effective_income / asking_rent) * 100
                ratios.append(f"• Collection Rate: {self.format_percentage(collection_rate)}")
            
            # Loss-to-Lease Rate
            if asking_rent and loss_to_lease and asking_rent > 0:
                loss_to_lease_pct = (abs(loss_to_lease) / asking_rent) * 100
                ratios.append(f"• Loss-to-Lease Rate: {self.format_percentage(loss_to_lease_pct)}")
            
            # Vacancy Rate
            if asking_rent and vacancy and asking_rent > 0:
                vacancy_rate = (abs(vacancy) / asking_rent) * 100
                ratios.append(f"• Vacancy Rate: {self.format_percentage(vacancy_rate)}")
            
            # Economic Occupancy Rate
            if gross_rent and effective_income and gross_rent > 0:
                economic_occupancy = (effective_income / gross_rent) * 100
                ratios.append(f"• Economic Occupancy Rate: {self.format_percentage(economic_occupancy)}")
            
            # NOI Margin (if we have NOI and effective income)
            if noi and effective_income and effective_income > 0:
                noi_margin = (noi / effective_income) * 100  
                ratios.append(f"• NOI Margin: {self.format_percentage(noi_margin)}")
            
            # Expense Ratio (if we have total expense and effective income)
            if total_expense and effective_income and effective_income > 0:
                expense_ratio = (abs(total_expense) / effective_income) * 100
                ratios.append(f"• Expense Ratio: {self.format_percentage(expense_ratio)}")
            
        except Exception as e:
            self.add_calculation_issue(f"Error calculating ratios: {str(e)}")
            ratios.append("• Error calculating performance ratios")
        
        return ratios
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """
        Get T12-specific metric categories.
        
        Returns:
            Dict[str, List[str]]: Categories and their metric patterns
        """
        return {
            "REVENUE_PERFORMANCE": [
                "Rent", "Income", "Gross Scheduled Rent", "Effective Rental Income", 
                "Other - Income", "Other Income", "Parking Garage Income", "Utility Income"
            ],
            "REVENUE_LOSS_FACTORS": [
                "Loss to lease", "Vacancy", "Concessions", "Delinquency", "Non Revenue Units"
            ],
            "EXPENSES": [
                "General & Admin.", "Management Fee", "Payroll", "Insurance", "Property Taxes",
                "Leasing & Marketing", "Professional fees", "Landscaping", "Security & Life Safety",
                "Repairs & Maintenance", "Unit T/O Refurbishment", "Utilities", "Trash Removal",
                "Miscellaneous", "Other - Expense", "Total Expense"
            ],
            "NOI_AND_BELOW_LINE": [
                "EBITDA (NOI)", "Repl. Reserve Fund", "State Franchise Fee", 
                "Partnership Professional Fees", "Asset Management Fees", "Debt Service",
                "Other - Below Line", "Total Below Line", "Renovations", "Monthly Cash Flow"
            ],
            "BALANCE_SHEET_ESCROW": [
                "Operating Account Balance", "Interest Reserve Account", "Undeposited Funds",
                "Security Deposits", "Total Cash", "Open ARR", "Escrow - Taxes",
                "Escrow - Insurance", "Escrow - Other", "Escrow - RR", "Open AP",
                "Total Equity", "Total Debt"
            ]
        }
    
    def _generate_ytd_summary(self, df: pd.DataFrame) -> List[str]:
        """
        Generate YTD (Year-To-Date) summary section.
        
        Args:
            df: Processed T12 DataFrame
            
        Returns:
            List[str]: YTD summary lines
        """
        ytd_data = self.get_ytd_data(df)
        if ytd_data.empty:
            return []
        
        summary_parts = []
        summary_parts.append("=== YEAR-TO-DATE (YTD) SUMMARY ===")
        
        # Categorize YTD metrics
        ytd_revenue_metrics = []
        ytd_expense_metrics = []
        ytd_other_metrics = []
        
        revenue_patterns = ["income", "rent", "revenue"]
        expense_patterns = ["expense", "cost", "fee", "tax", "insurance", "maintenance", "utility"]
        
        for _, row in ytd_data.iterrows():
            metric = row['Metric']
            value = row['Value']
            formatted_line = f"• {metric}: {self.format_currency(value)}"
            
            # Categorize based on metric name
            metric_lower = metric.lower()
            if any(pattern in metric_lower for pattern in revenue_patterns):
                ytd_revenue_metrics.append(formatted_line)
            elif any(pattern in metric_lower for pattern in expense_patterns):
                ytd_expense_metrics.append(formatted_line)
            else:
                ytd_other_metrics.append(formatted_line)
        
        # Display categorized YTD metrics
        if ytd_revenue_metrics:
            summary_parts.append("CUMULATIVE YTD REVENUE & INCOME (Jan 1st to present):")
            summary_parts.extend(ytd_revenue_metrics)
            summary_parts.append("")
        
        if ytd_expense_metrics:
            summary_parts.append("CUMULATIVE YTD EXPENSES (Jan 1st to present):")
            summary_parts.extend(ytd_expense_metrics)
            summary_parts.append("")
        
        if ytd_other_metrics:
            summary_parts.append("CUMULATIVE YTD OTHER METRICS (Jan 1st to present):")
            summary_parts.extend(ytd_other_metrics)
            summary_parts.append("")
        
        return summary_parts
