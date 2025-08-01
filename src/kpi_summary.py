"""
Generate KPI summary from cleaned T12 DataFrame
Enhanced to work with the robust preprocessing output
"""
import pandas as pd

def generate_kpi_summary(df):
    """
    Generate standardized KPI summary for T12 property data.
    Input: Long-format DataFrame with columns: [Sheet, Metric, Month, MonthParsed, IsYTD, Value, Year, Month_Name, Is_Negative]
    """
    try:
        summary_parts = []
        
        # Filter out YTD data for latest month analysis
        monthly_data = df[~df["IsYTD"]].copy()
        
        # Get latest month data
        if monthly_data.empty:
            return "No monthly data found to analyze."
        
        latest_month = monthly_data["MonthParsed"].max()
        latest_data = monthly_data[monthly_data["MonthParsed"] == latest_month]
        
        # Add header with analysis period
        summary_parts.append(f"=== T12 PROPERTY ANALYSIS - {latest_month.strftime('%B %Y')} ===")
        summary_parts.append(f"Sheet: {df['Sheet'].iloc[0]}")
        summary_parts.append("")
        
        # Key Revenue Metrics
        summary_parts.append("=== REVENUE PERFORMANCE ===")
        
        # Property Asking Rent
        asking_rent = get_metric_value(latest_data, 'Property Asking Rent')
        if asking_rent is not None:
            summary_parts.append(f"• Property Asking Rent: ${asking_rent:,.2f}")
        
        # Effective Rental Income
        effective_income = get_metric_value(latest_data, 'Effective Rental Income')
        if effective_income is not None:
            summary_parts.append(f"• Effective Rental Income: ${effective_income:,.2f}")
            
        # Gross Scheduled Rent
        gross_rent = get_metric_value(latest_data, 'Gross Scheduled Rent')
        if gross_rent is not None:
            summary_parts.append(f"• Gross Scheduled Rent: ${gross_rent:,.2f}")
        
        # Loss Factors
        summary_parts.append("\n=== REVENUE LOSS FACTORS ===")
        
        loss_metrics = ['Loss to lease', 'Vacancy', 'Concessions', 'Delinquency', 'Non Revenue Units']
        for metric in loss_metrics:
            value = get_metric_value(latest_data, metric)
            if value is not None:
                summary_parts.append(f"• {metric}: ${value:,.2f}")
        
        # Other Income
        summary_parts.append("\n=== OTHER INCOME SOURCES ===")
        
        other_income_metrics = ['Parking Garage Income', 'Utility Income', 'Other - Income', 'Other Income']
        for metric in other_income_metrics:
            value = get_metric_value(latest_data, metric)
            if value is not None and value != 0:
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
            summary_parts.append("\n=== YEAR-TO-DATE SUMMARY ===")
            ytd_effective_income = get_metric_value(ytd_data, 'Effective Rental Income')
            if ytd_effective_income is not None:
                summary_parts.append(f"• YTD Effective Rental Income: ${ytd_effective_income:,.2f}")
        
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
