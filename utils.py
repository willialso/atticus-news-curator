#!/usr/bin/env python3
"""
Utility functions for Atticus News Curator
Manual operations and maintenance tasks
"""

import os
import json
from datetime import datetime, timedelta
from main import AttticusNewsCurator

def manual_curation_run():
    """Run a manual curation cycle"""
    print("🚀 Starting manual curation run...")
    
    try:
        curator = AttticusNewsCurator()
        curator.run_curation()
        print("✅ Manual curation completed successfully")
    except Exception as e:
        print(f"❌ Manual curation failed: {e}")

def view_recent_articles():
    """View recent articles in the Google Sheet"""
    try:
        curator = AttticusNewsCurator()
        
        # Get last 10 rows
        all_values = curator.sheet.get_all_values()
        recent_rows = all_values[-10:] if len(all_values) > 10 else all_values[1:]
        
        print("📊 Recent articles in Google Sheets:")
        print("-" * 80)
        
        for i, row in enumerate(recent_rows, 1):
            if len(row) >= 3:
                date_added = row[0] if row[0] else "No date"
                sample_copy = row[2][:60] + "..." if len(row[2]) > 60 else row[2]
                print(f"{i}. {date_added}: {sample_copy}")
        
    except Exception as e:
        print(f"❌ Failed to view articles: {e}")

def clear_processed_cache():
    """Clear the processed articles cache"""
    try:
        curator = AttticusNewsCurator()
        curator.processed_articles.clear()
        print("✅ Processed articles cache cleared")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}")

def test_single_feed(feed_url):
    """Test fetching from a single RSS feed"""
    try:
        curator = AttticusNewsCurator()
        articles = curator.fetch_articles_from_feed(feed_url)
        
        print(f"📰 Results from {feed_url}:")
        print(f"Found {len(articles)} relevant articles")
        
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title'][:60]}... (Score: {article['score']})")
            
    except Exception as e:
        print(f"❌ Feed test failed: {e}")

def export_sheet_data():
    """Export current sheet data to JSON"""
    try:
        curator = AttticusNewsCurator()
        all_values = curator.sheet.get_all_values()
        
        # Convert to list of dictionaries
        if all_values:
            headers = all_values[0]
            data = []
            
            for row in all_values[1:]:
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                data.append(row_dict)
            
            # Save to file
            filename = f"sheet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"✅ Sheet data exported to {filename}")
            print(f"📊 Exported {len(data)} rows")
        else:
            print("📭 No data found in sheet")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")

def show_menu():
    """Show interactive menu"""
    print("\\n🔧 Atticus News Curator - Utility Menu")
    print("=" * 50)
    print("1. Run manual curation")
    print("2. View recent articles") 
    print("3. Clear processed cache")
    print("4. Test single RSS feed")
    print("5. Export sheet data")
    print("6. Exit")
    print("=" * 50)

def main():
    """Interactive utility menu"""
    while True:
        show_menu()
        choice = input("\\nSelect option (1-6): ").strip()
        
        if choice == '1':
            manual_curation_run()
        elif choice == '2':
            view_recent_articles()
        elif choice == '3':
            clear_processed_cache()
        elif choice == '4':
            feed_url = input("Enter RSS feed URL: ").strip()
            if feed_url:
                test_single_feed(feed_url)
        elif choice == '5':
            export_sheet_data()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()'''

print(utils_py)
