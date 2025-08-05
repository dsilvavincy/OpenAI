#!/usr/bin/env python3

# Debug the exact line-by-line parsing
import sys
sys.path.append('src')

from core.output_quality import OutputFormatter

# Test with your actual response content
test_content = """## 4️⃣ Strategic Management Questions
1. Why did Net Operating Income decrease from $96.52 to $86.42 (10.5% change)?
2. How can we address the increasing Total Expense performance of $-110.15 vs industry benchmark?
3. What caused the Delinquency Rate variance to remain stable at 1.96% this month?
4. Should we investigate the Rent trend showing $234.33 vs $219.59 for Asking and Scheduled Rents?
5. How do we optimize Property Taxes currently at $-31.34?

## 5️⃣ Actionable Recommendations (NOI Improvement)
- **Target Effective Rental Income:** Currently $178.43, increase by 5.00% to add $8.92 to monthly NOI.
- **Reduce Payroll Expense:** Currently $-26.01, reduce by 10.00% to save $2.60 monthly.
- **Address Total Expense:** At $-110.15 (55.98% of income), implement stringent cost control measures.

## 6️⃣ Red Flags / Immediate Attention
- **Net Operating Income** decreased significantly, representing a revenue/expenditure imbalance - requires immediate analysis.
- **Professional fees** at $0 should typically reflect market rate expenses based on consultant engagements."""

formatter = OutputFormatter()

# Let's manually trace the parsing
lines = test_content.split('\n')
current_section = None

print("=== LINE BY LINE PARSING DEBUG ===")
for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
        
    line_upper = line.upper()
    
    # Check what section this line would trigger
    section_triggered = None
    
    if ('4️⃣' in line or 
        ('QUESTION' in line_upper and ('STRATEGIC' in line_upper or 'MANAGEMENT' in line_upper))):
        section_triggered = 'questions'
    elif ('5️⃣' in line or 
          ('RECOMMENDATION' in line_upper or 'ACTIONABLE' in line_upper)):
        section_triggered = 'recommendations'
    elif ('6️⃣' in line or '⚠️' in line or
          ('CONCERN' in line_upper or 'TREND' in line_upper or 'RED FLAG' in line_upper or 
           'IMMEDIATE ATTENTION' in line_upper or 'RED FLAGS' in line_upper)):
        section_triggered = 'concerns'
    elif line.startswith('##'):
        section_triggered = 'RESET'
    
    if section_triggered:
        current_section = section_triggered if section_triggered != 'RESET' else None
        print(f"Line {i+1}: '{line}' -> Section: {current_section}")
    elif current_section and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith(('-', '*', '•'))):
        print(f"Line {i+1}: '{line}' -> Adding to {current_section}")
