"""
Trilakes.co SEO Monitoring Script
Run weekly to track indexing progress and performance.

Usage: python seo_monitor.py
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
import os

# Config
GSC_KEY = r'C:\Users\17192\OneDrive\Desktop\Dgen\gsc-key.json'
SITE_URL = 'sc-domain:trilakes.co'
LOG_FILE = r'C:\Users\17192\OneDrive\Desktop\trilakes-blog\seo_history.json'
TOTAL_PAGES = 1220  # Your total blog pages

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        GSC_KEY,
        scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )
    return build('searchconsole', 'v1', credentials=creds)

def get_date_range(days_back=7):
    end = datetime.now() - timedelta(days=3)  # GSC has 3-day delay
    start = end - timedelta(days=days_back)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

def get_metrics(service, start_date, end_date):
    """Get overall metrics for date range"""
    try:
        r = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={'startDate': start_date, 'endDate': end_date, 'dimensions': []}
        ).execute()
        if r.get('rows'):
            return {
                'clicks': int(r['rows'][0]['clicks']),
                'impressions': int(r['rows'][0]['impressions']),
                'ctr': round(r['rows'][0]['ctr'] * 100, 2),
                'position': round(r['rows'][0]['position'], 1)
            }
    except:
        pass
    return {'clicks': 0, 'impressions': 0, 'ctr': 0, 'position': 0}

def get_pages_with_impressions(service, start_date, end_date):
    """Count pages getting any impressions"""
    try:
        r = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': 2000
            }
        ).execute()
        return len(r.get('rows', []))
    except:
        return 0

def get_top_pages(service, start_date, end_date, limit=10):
    """Get top performing pages"""
    try:
        r = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': limit
            }
        ).execute()
        pages = []
        for row in r.get('rows', []):
            url = row['keys'][0].replace('https://trilakes.co', '')
            pages.append({
                'url': url[:50] + '...' if len(url) > 50 else url,
                'clicks': int(row['clicks']),
                'impressions': int(row['impressions']),
                'position': round(row['position'], 1)
            })
        return pages
    except:
        return []

def get_top_queries(service, start_date, end_date, limit=10):
    """Get top search queries"""
    try:
        r = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': limit
            }
        ).execute()
        queries = []
        for row in r.get('rows', []):
            queries.append({
                'query': row['keys'][0][:40],
                'clicks': int(row['clicks']),
                'impressions': int(row['impressions']),
                'position': round(row['position'], 1)
            })
        return queries
    except:
        return []

def load_history():
    """Load historical data"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return {'reports': []}

def save_history(history):
    """Save historical data"""
    with open(LOG_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def main():
    print("=" * 60)
    print("TRILAKES.CO SEO MONITOR")
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    service = get_service()
    
    # This week (last 7 days)
    this_start, this_end = get_date_range(7)
    this_week = get_metrics(service, this_start, this_end)
    
    # Last week (7-14 days ago)
    last_start, last_end = get_date_range(14)
    last_week_end = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
    last_week = get_metrics(service, last_start, last_week_end)
    
    # Pages indexed
    pages_visible = get_pages_with_impressions(service, this_start, this_end)
    visibility_pct = round(pages_visible / TOTAL_PAGES * 100, 1)
    
    # Calculate changes
    click_change = this_week['clicks'] - last_week['clicks']
    impr_change = this_week['impressions'] - last_week['impressions']
    
    print(f"\n📊 THIS WEEK ({this_start} to {this_end})")
    print(f"   Clicks:      {this_week['clicks']:>6} ({'+' if click_change >= 0 else ''}{click_change} vs last week)")
    print(f"   Impressions: {this_week['impressions']:>6} ({'+' if impr_change >= 0 else ''}{impr_change} vs last week)")
    print(f"   CTR:         {this_week['ctr']:>5}%")
    print(f"   Avg Position:{this_week['position']:>6}")
    
    print(f"\n📈 INDEXING PROGRESS")
    print(f"   Pages with impressions: {pages_visible} / {TOTAL_PAGES}")
    print(f"   Visibility: {visibility_pct}%")
    print(f"   {'█' * int(visibility_pct // 2)}{'░' * (50 - int(visibility_pct // 2))} {visibility_pct}%")
    
    # Top pages
    print(f"\n🏆 TOP 5 PAGES (by clicks)")
    for i, p in enumerate(get_top_pages(service, this_start, this_end, 5), 1):
        print(f"   {i}. {p['url']}")
        print(f"      {p['clicks']} clicks, {p['impressions']} impr, pos {p['position']}")
    
    # Top queries
    print(f"\n🔍 TOP 5 QUERIES (by clicks)")
    for i, q in enumerate(get_top_queries(service, this_start, this_end, 5), 1):
        print(f"   {i}. \"{q['query']}\"")
        print(f"      {q['clicks']} clicks, {q['impressions']} impr, pos {q['position']}")
    
    # Save to history
    history = load_history()
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'period': f"{this_start} to {this_end}",
        'clicks': this_week['clicks'],
        'impressions': this_week['impressions'],
        'ctr': this_week['ctr'],
        'position': this_week['position'],
        'pages_visible': pages_visible,
        'visibility_pct': visibility_pct
    }
    history['reports'].append(report)
    save_history(history)
    
    # Show trend if we have history
    if len(history['reports']) > 1:
        print(f"\n📉 HISTORICAL TREND")
        print(f"   {'Date':<12} {'Clicks':<8} {'Impr':<8} {'Pages':<8} {'Visibility'}")
        print(f"   {'-'*50}")
        for r in history['reports'][-5:]:  # Last 5 reports
            print(f"   {r['date']:<12} {r['clicks']:<8} {r['impressions']:<8} {r['pages_visible']:<8} {r['visibility_pct']}%")
    
    print(f"\n✅ Report saved to: {LOG_FILE}")
    print("=" * 60)

if __name__ == '__main__':
    main()
