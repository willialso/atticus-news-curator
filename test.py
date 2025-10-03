#!/usr/bin/env python3
"""
Test script for Atticus News Curator
Run this to test your setup before deploying to Render
"""

import os
import sys
from main import AttticusNewsCurator

def test_environment_variables():
    """Test if all required environment variables are set"""
    required_vars = [
        'GOOGLE_PROJECT_ID',
        'GOOGLE_PRIVATE_KEY_ID',
        'GOOGLE_PRIVATE_KEY', 
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_CERT_URL',
        'GOOGLE_SHEET_ID'
    ]
    
    print("🔍 Testing environment variables...")
    missing_vars = []
    
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
            
    if missing_vars:
        print(f"❌ Missing variables: {missing_vars}")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_google_sheets_connection():
    """Test Google Sheets API connection"""
    try:
        print("🔍 Testing Google Sheets connection...")
        curator = AttticusNewsCurator()
        
        # Try to read first row
        headers = curator.sheet.row_values(1)
        print(f"✅ Successfully connected to Google Sheets")
        print(f"📊 Sheet headers: {headers}")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False

def test_rss_feeds():
    """Test RSS feed accessibility"""
    import feedparser
    import time
    
    feeds = [
        'https://cointelegraph.com/rss',
        'https://decrypt.co/feed',
        'https://blockworks.co/feed'
    ]
    
    print("🔍 Testing RSS feeds...")
    working_feeds = 0
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                print(f"✅ {feed_url}: {len(feed.entries)} articles")
                working_feeds += 1
            else:
                print(f"⚠️ {feed_url}: No articles found")
        except Exception as e:
            print(f"❌ {feed_url}: {e}")
        
        time.sleep(0.5)
    
    print(f"📊 {working_feeds}/{len(feeds)} feeds working")
    return working_feeds > 0

def test_article_scoring():
    """Test the article scoring system"""
    print("🔍 Testing article scoring...")
    
    test_articles = [
        {
            'title': 'Bitcoin Options Trading Surges as Institutional Demand Grows',
            'summary': 'Major exchanges report increased bitcoin options volume from hedge funds seeking downside protection.'
        },
        {
            'title': 'New DeFi Protocol Launches Perpetual Futures',  
            'summary': 'Platform offers crypto derivatives with automated hedging strategies for retail traders.'
        },
        {
            'title': 'General Crypto News Article',
            'summary': 'Some general cryptocurrency news that is not very relevant to options trading.'
        }
    ]
    
    try:
        curator = AttticusNewsCurator()
        
        for i, article in enumerate(test_articles, 1):
            score, keywords = curator.calculate_article_score(
                article['title'], 
                article['summary']
            )
            
            print(f"Article {i}:")
            print(f"  Title: {article['title'][:60]}...")
            print(f"  Score: {score}")
            print(f"  Keywords: {', '.join(keywords[:3])}")
            print(f"  Passes threshold: {'✅' if score >= 8 else '❌'}")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        return False

def run_full_test():
    """Run complete test suite"""
    print("🚀 Starting Atticus News Curator Test Suite\\n")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Google Sheets Connection", test_google_sheets_connection), 
        ("RSS Feed Access", test_rss_feeds),
        ("Article Scoring", test_article_scoring)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"TEST: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print(f"{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️ Some tests failed. Fix issues before deploying.")

if __name__ == "__main__":
    run_full_test()'''

print(test_py)
