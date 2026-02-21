"""
Test script demonstrating Excel export functionality
Run: python test_export_demo.py
"""

import sys
sys.path.insert(0, '/workspaces/Scheduling/backend')

from app.excel_exporter import ExcelExporter
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta

def demo_export():
    """Demonstrate the Excel export functionality"""
    
    db = SessionLocal()
    
    print("=" * 80)
    print("CAMPUS SCHEDULING SYSTEM - EXCEL EXPORT DEMO")
    print("=" * 80)
    print()
    
    try:
        # Check if there are any schedule runs
        schedule_runs = db.query(models.ScheduleRun).all()
        
        if not schedule_runs:
            print("⚠️  No schedule runs found in database.")
            print()
            print("To test the export functionality:")
            print("1. Add master data via the React dashboard at http://localhost:3000/master-data")
            print("2. Create a schedule run and add schedule entries")
            print("3. Then run this script again")
            print()
            return
        
        # Display available schedule runs
        print(f"Found {len(schedule_runs)} schedule run(s) in database:")
        print()
        
        for run in schedule_runs:
            entry_count = db.query(models.ScheduleEntry).filter(
                models.ScheduleEntry.schedule_run_id == run.id
            ).count()
            
            print(f"  Run ID: {run.id}")
            print(f"  Term: {run.term_id}")
            print(f"  Status: {run.status}")
            print(f"  Score: {run.objective_score}")
            print(f"  Entries: {entry_count}")
            print(f"  Created: {run.created_at}")
            print()
        
        # Export the first schedule run
        first_run = schedule_runs[0]
        run_id = first_run.id
        
        print(f"📊 Exporting schedule run {run_id}...")
        print()
        
        # Create exporter
        exporter = ExcelExporter(db)
        
        # Generate Excel
        excel_bytes = exporter.export_schedule(
            run_id,
            institution_name="Campus University"
        )
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"schedule_{run_id}_{timestamp}.xlsx"
        
        with open(filename, "wb") as f:
            f.write(excel_bytes)
        
        print(f"✅ Export successful!")
        print()
        print(f"📁 File saved: {filename}")
        print(f"📊 File size: {len(excel_bytes) / 1024:.1f} KB")
        print()
        print("Sheets included:")
        print("  1. Teacher View - Schedule per teacher")
        print("  2. Section View - Schedule per course section")
        print("  3. Room View - Schedule by building and room")
        print("  4. Checklist - Validation report")
        print()
        print("Color coding: Each course is assigned a unique color")
        print()
        
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print("=" * 80)

if __name__ == "__main__":
    demo_export()
