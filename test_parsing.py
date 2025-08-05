#!/usr/bin/env python3

# Quick test to debug the parsing issue
import sys
sys.path.append('src')

from core.output_quality import OutputFormatter

# Test with your actual response content
test_content = """
## 4️⃣ Strategic Management Questions
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
- **Professional fees** at $0 should typically reflect market rate expenses based on consultant engagements.
"""

formatter = OutputFormatter()
sections = formatter._extract_sections(test_content)

print("=== PARSING TEST RESULTS ===")
print(f"Strategic Questions found: {len(sections['questions'])}")
for i, q in enumerate(sections['questions'], 1):
    print(f"  {i}. {q}")

print(f"\nRecommendations found: {len(sections['recommendations'])}")
for i, r in enumerate(sections['recommendations'], 1):
    print(f"  {i}. {r}")

print(f"\nConcerns found: {len(sections['concerns'])}")
for i, c in enumerate(sections['concerns'], 1):
    print(f"  {i}. {c}")
