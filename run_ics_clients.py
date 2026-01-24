"""
ICS Analysis - Monthly Client Runner

Update the ics_not_in_dump values each month, then run this script.
Comment out clients you're not running this month.

Usage:
    python run_ics_clients.py
"""

import sys
sys.path.append(r'C:\Users\james.gilmore\OneDrive - Computer Services, Inc\Desktop\ARS\ARS Analysis\Scripts')

from ics_analysis import run_client

# =============================================================================
# MONTHLY RUNS - Update ics_not_in_dump each month
# =============================================================================

# Client 1453 - Connex CU
run_client("1453", ics_not_in_dump=80, export_pptx=True)

# Client 1615 - Sample CU
# run_client("1615", ics_not_in_dump=100, export_pptx=True)

# Client 1776 - Another CU
# run_client("1776", ics_not_in_dump=0, export_pptx=True)

# Add more clients as needed:
# run_client("XXXX", ics_not_in_dump=0, export_pptx=True)


# =============================================================================
print("\n" + "="*70)
print("✅ ALL CLIENTS COMPLETE")
print("="*70)
