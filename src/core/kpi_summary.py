"""
Generate KPI summary from cleaned T12 DataFrame
Enhanced to work with the robust preprocessing output
"""
import pandas as pd

def generate_kpi_summary(df):
    """
    Generate a comprehensive KPI summary for T12 property data.
    Dynamically includes all metrics found in the file, grouped by logical categories.
    """
    try:
        summary_parts = []
        monthly_data = df[~df["IsYTD"]].copy()
        if monthly_data.empty:
            return "No monthly data found to analyze."
        latest_month = monthly_data["MonthParsed"].max()
        latest_data = monthly_data[monthly_data["MonthParsed"] == latest_month]
        summary_parts.append(f"=== T12 PROPERTY ANALYSIS - {latest_month.strftime('%B %Y')} ===")
        summary_parts.append(f"Sheet: {df['Sheet'].iloc[0]}")
        summary_parts.append("")

        # Group metrics by logical categories
        categories = {
            "REVENUE PERFORMANCE": ["Rent", "Income", "Gross Scheduled Rent", "Effective Rental Income", "Other - Income", "Other Income"],
            "REVENUE LOSS FACTORS": ["Loss to lease", "Vacancy", "Concessions", "Delinquency", "Non Revenue Units"],
            "EXPENSES": ["General & Admin.", "Management Fee", "Payroll", "Insurance", "Property Taxes", "Leasing & Marketing", "Professional fees", "Landscaping", "Security & Life Safety", "Repairs & Maintenance", "Unit T/O Refurbishment", "Utilities", "Trash Removal", "Miscellaneous", "Other - Expense", "Total Expense"],
            "NOI & BELOW LINE": ["EBITDA (NOI)", "Repl. Reserve Fund", "State Franchise Fee", "Partnership Professional Fees", "Asset Management Fees", "Debt Service", "Other - Below Line", "Total Below Line", "Renovations", "Monthly Cash Flow"],
            "BALANCE SHEET & ESCROW": ["Operating Account Balance", "Interest Reserve Account", "Undeposited Funds", "Security Deposits", "Total Cash", "Open ARR", "Escrow - Taxes", "Escrow - Insurance", "Escrow - Other", "Escrow - RR", "Open AP", "Total Equity", "Total Debt"]
        }

        # Find all unique metrics in the file
        all_metrics = latest_data["Metric"].unique()
        used_metrics = set()

        # Print each category
        for cat, patterns in categories.items():
            cat_metrics = []
            for pattern in patterns:
                for metric in all_metrics:
                    if pattern.lower().replace(" ", "") in metric.lower().replace(" ", "") and metric not in used_metrics:
                        value = get_metric_value(latest_data, metric)
                        if value is not None:
                            cat_metrics.append(f"• {metric}: ${value:,.2f}")
                            used_metrics.add(metric)
            if cat_metrics:
                summary_parts.append(f"=== {cat} ===")
                summary_parts.extend(cat_metrics)

        # Any remaining metrics not categorized
        uncategorized = [m for m in all_metrics if m not in used_metrics]
        if uncategorized:
            summary_parts.append("=== OTHER METRICS ===")
            for metric in uncategorized:
                value = get_metric_value(latest_data, metric)
                if value is not None:
                    summary_parts.append(f"• {metric}: ${value:,.2f}")

        # Trend Analysis
        summary_parts.append("\n=== TREND ANALYSIS ===")
        trend_analysis = analyze_trends(monthly_data)
        if trend_analysis:
            summary_parts.extend(trend_analysis)
        else:
            summary_parts.append("• Insufficient data for trend analysis")

        # Performance Ratios
        summary_parts.append("\n=== KEY PERFORMANCE RATIOS ===")
        ratios = calculate_ratios(latest_data)
        if ratios:
            summary_parts.extend(ratios)
        else:
            summary_parts.append("• Unable to calculate performance ratios")

        # YTD Summary if available
        ytd_data = df[df["IsYTD"]]
        if not ytd_data.empty:
            summary_parts.append("\n=== YEAR-TO-DATE (YTD) CUMULATIVE TOTALS ===")
            summary_parts.append("CRITICAL: YTD = Year-To-Date CUMULATIVE totals from January 1st to present.")
            summary_parts.append("YTD IS NOT A MONTH - it represents accumulated totals, not monthly amounts.")
            summary_parts.append("Use YTD for annual performance analysis, NOT for month-to-month trending.")
            summary_parts.append("")
            
            # Group YTD metrics by category for better context
            ytd_revenue_metrics = []
            ytd_expense_metrics = []
            ytd_other_metrics = []
            
            for metric in ytd_data["Metric"].unique():
                value = get_metric_value(ytd_data, metric)
                if value is not None:
                    formatted_line = f"• {metric} (CUMULATIVE YTD): ${value:,.2f}"
                    
                    # Categorize YTD metrics
                    metric_lower = metric.lower()
                    if any(word in metric_lower for word in ['income', 'rent', 'revenue']):
                        ytd_revenue_metrics.append(formatted_line)
                    elif any(word in metric_lower for word in ['expense', 'cost', 'fee', 'tax', 'payroll']):
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

        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error generating KPI summary: {str(e)}"

def get_metric_value(data, metric_name):
    """Get value for a specific metric from the data"""
    try:
        # Try exact match first
        exact_match = data[data['Metric'] == metric_name]['Value']
        if len(exact_match) > 0:
            return exact_match.iloc[0]
        
        # Try partial match if exact match fails
        partial_match = data[data['Metric'].str.contains(metric_name, case=False, na=False)]['Value']
        if len(partial_match) > 0:
            return partial_match.iloc[0]
        
        return None
    except:
        return None

def analyze_trends(monthly_data):
    """Analyze month-over-month trends for key metrics"""
    trends = []
    
    key_metrics = ['Effective Rental Income', 'Property Asking Rent', 'Vacancy', 'Delinquency', 'Loss to lease']
    
    for metric in key_metrics:
        try:
            # Get data for this metric across all months
            metric_data = monthly_data[
                monthly_data['Metric'].str.contains(metric, case=False, na=False)
            ].copy()
            
            if len(metric_data) >= 2:
                # Sort by month and calculate change
                metric_data = metric_data.sort_values('MonthParsed')
                values = metric_data['Value'].tolist()
                
                if len(values) >= 2:
                    latest = values[-1]
                    previous = values[-2]
                    change = latest - previous
                    pct_change = (change / abs(previous)) * 100 if previous != 0 else 0
                    
                    direction = "increased" if change > 0 else "decreased"
                    trends.append(f"• {metric}: {direction} by ${abs(change):,.2f} ({abs(pct_change):.1f}%)")
        except Exception as e:
            continue  # Skip metrics that cause errors
    
    return trends

def calculate_ratios(latest_data):
    """Calculate key performance ratios"""
    ratios = []
    
    try:
        asking_rent = get_metric_value(latest_data, 'Property Asking Rent')
        effective_income = get_metric_value(latest_data, 'Effective Rental Income')
        gross_rent = get_metric_value(latest_data, 'Gross Scheduled Rent')
        loss_to_lease = get_metric_value(latest_data, 'Loss to lease')
        vacancy = get_metric_value(latest_data, 'Vacancy')
        
        # Collection Rate (Effective Income / Asking Rent)
        if asking_rent and effective_income and asking_rent > 0:
            collection_rate = (effective_income / asking_rent) * 100
            ratios.append(f"• Collection Rate: {collection_rate:.1f}%")
        
        # Loss-to-Lease Rate
        if asking_rent and loss_to_lease and asking_rent > 0:
            loss_to_lease_pct = (abs(loss_to_lease) / asking_rent) * 100
            ratios.append(f"• Loss-to-Lease Rate: {loss_to_lease_pct:.1f}%")
            
        # Vacancy Rate
        if asking_rent and vacancy and asking_rent > 0:
            vacancy_rate = (abs(vacancy) / asking_rent) * 100
            ratios.append(f"• Vacancy Rate: {vacancy_rate:.1f}%")
        
        # Economic Occupancy Rate (if we have gross rent)
        if gross_rent and effective_income and gross_rent > 0:
            economic_occupancy = (effective_income / gross_rent) * 100
            ratios.append(f"• Economic Occupancy Rate: {economic_occupancy:.1f}%")
            
    except Exception as e:
        ratios.append(f"• Error calculating ratios: {str(e)}")
    
    return ratios
