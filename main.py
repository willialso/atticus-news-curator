#!/usr/bin/env python3
"""
Atticus News Curator - Automated crypto/options news aggregator
Runs on Render Background Worker, updates Google Sheets daily
Focused on Bitcoin options, perpetual futures, and institutional adoption
"""

import os
import time
import schedule
import logging
import requests
import feedparser
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.service_account import Credentials
import gspread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AttticusNewsCurator:
    def __init__(self):
        """Initialize the news curator with Google Sheets and RSS feeds"""
        self.setup_google_sheets()
        
        # Keywords with weights optimized for your options trading platform
        self.keywords = {
            'bitcoin options': 15,
            'crypto options': 12, 
            'btc options': 15,
            'perpetual futures': 10,
            'defi options': 10,
            'downside protection': 8,
            'institutional crypto': 8,
            'crypto derivatives': 9,
            'btc etf': 7,
            'volatility trading': 8,
            'options trading': 12,
            'web3': 5,
            'hedging strategies': 7,
            'risk management': 6,
            'crypto volatility': 6,
            'institutional adoption': 7,
            'derivatives market': 8,
            'digital assets': 4,
            'crypto hedge': 6,
            'portfolio protection': 7,
            'trading infrastructure': 6,
            'market making': 7,
            'liquidity provision': 6,
            'automated trading': 5,
            'algorithmic trading': 5
        }
        
        # Premium crypto news RSS feeds
        self.feeds = [
            'https://cointelegraph.com/rss',
            'https://decrypt.co/feed', 
            'https://blockworks.co/feed',
            'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'https://thedefiant.io/feed',
            'https://cryptonews.com/news/feed',
            'https://www.theblockcrypto.com/rss.xml',
            'https://bitcoinmagazine.com/.rss/full/'
        ]
        
        # Track processed articles to avoid duplicates
        self.processed_articles = set()
        
    def setup_google_sheets(self):
        """Setup Google Sheets connection using environment variables"""
        try:
            # Build credentials dictionary from environment variables
            creds_info = {
                "type": "service_account",
                "project_id": os.environ['GOOGLE_PROJECT_ID'],
                "private_key_id": os.environ['GOOGLE_PRIVATE_KEY_ID'], 
                "private_key": os.environ['GOOGLE_PRIVATE_KEY'].replace('\\\\n', '\\n'),
                "client_email": os.environ['GOOGLE_CLIENT_EMAIL'],
                "client_id": os.environ['GOOGLE_CLIENT_ID'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ['GOOGLE_CLIENT_CERT_URL']
            }
            
            # Define required scopes for Google Sheets and Drive access
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Create credentials and authorize gspread client
            credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
            self.gc = gspread.authorize(credentials)
            
            # Open the specific Google Sheet by ID
            sheet_id = os.environ['GOOGLE_SHEET_ID']
            self.sheet = self.gc.open_by_key(sheet_id).sheet1
            
            logger.info("✅ Google Sheets connected successfully")
            
            # Test connection by reading first row
            headers = self.sheet.row_values(1)
            logger.info(f"📊 Sheet headers: {headers}")
            
        except KeyError as e:
            logger.error(f"❌ Missing environment variable: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Google Sheets setup failed: {e}")
            raise
            
    def clean_text(self, text: str) -> str:
        """Clean HTML tags and excessive whitespace from text"""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\\s+', ' ', text)
        
        # Remove special characters that might break CSV
        text = text.replace('"', "'").replace('\\n', ' ').replace('\\r', ' ')
        
        return text.strip()
        
    def calculate_article_score(self, title: str, summary: str) -> tuple:
        """Calculate relevance score for an article based on keywords"""
        content = f"{title} {summary}".lower()
        score = 0
        matched_keywords = []
        
        # Score based on keyword matches
        for keyword, weight in self.keywords.items():
            if keyword in content:
                score += weight
                matched_keywords.append(keyword)
                
        # Bonus points for multiple keyword matches
        if len(matched_keywords) > 1:
            score += len(matched_keywords) * 2
            
        # Bonus for title matches (more visible)
        title_lower = title.lower()
        for keyword in self.keywords:
            if keyword in title_lower:
                score += 3
                
        return score, matched_keywords
        
    def create_sample_copy(self, title: str, summary: str, max_length: int = 140) -> str:
        """Create concise sample copy for social media/content use"""
        # Clean the summary text
        clean_summary = self.clean_text(summary)
        
        # If summary is too short, use title + summary
        if len(clean_summary) < 50:
            combined = f"{title}. {clean_summary}"
        else:
            combined = clean_summary
            
        # Truncate to max length with ellipsis
        if len(combined) > max_length:
            return combined[:max_length-3] + "..."
        else:
            return combined
            
    def fetch_articles_from_feed(self, feed_url: str) -> List[Dict]:
        """Fetch articles from a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"📰 Fetching from: {feed_url}")
            
            # Parse RSS feed with timeout
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logger.warning(f"⚠️ No entries found in feed: {feed_url}")
                return articles
                
            # Process recent articles (last 10 from each feed)
            for entry in feed.entries[:10]:
                try:
                    # Skip if we've already processed this article
                    article_id = entry.get('id', entry.link)
                    if article_id in self.processed_articles:
                        continue
                        
                    # Extract article data
                    title = self.clean_text(entry.title)
                    summary = self.clean_text(entry.get('summary', entry.get('description', '')))
                    
                    # Calculate relevance score
                    score, matched_keywords = self.calculate_article_score(title, summary)
                    
                    # Only include articles with sufficient relevance (score >= 8)
                    if score >= 8:
                        sample_copy = self.create_sample_copy(title, summary)
                        
                        articles.append({
                            'id': article_id,
                            'title': title,
                            'link': entry.link,
                            'sample_copy': sample_copy,
                            'score': score,
                            'matched_keywords': matched_keywords,
                            'published': entry.get('published', 'Unknown'),
                            'source': feed.feed.get('title', 'Unknown Source')
                        })
                        
                        # Mark as processed
                        self.processed_articles.add(article_id)
                        
                except Exception as e:
                    logger.error(f"❌ Error processing entry from {feed_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error fetching feed {feed_url}: {e}")
            
        return articles
        
    def fetch_all_articles(self) -> List[Dict]:
        """Fetch articles from all RSS feeds"""
        all_articles = []
        
        for feed_url in self.feeds:
            try:
                articles = self.fetch_articles_from_feed(feed_url)
                all_articles.extend(articles)
                
                # Rate limiting to be respectful to RSS servers
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch from {feed_url}: {e}")
                continue
                
        # Sort by relevance score (highest first)
        all_articles.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top articles (max 5 per run to avoid overwhelming the sheet)
        return all_articles[:5]
        
    def add_articles_to_sheet(self, articles: List[Dict]):
        """Add curated articles to Google Sheets"""
        if not articles:
            logger.info("📝 No articles to add today")
            return
            
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            added_count = 0
            
            for article in articles:
                try:
                    # Prepare row data matching your sheet format
                    row_data = [
                        today,                      # Date Added
                        article['link'],            # Reference Link  
                        article['sample_copy'],     # Sample Copy
                        '',                         # Empty column 1
                        '',                         # Empty column 2
                        ''                          # Empty column 3
                    ]
                    
                    # Add row to sheet
                    self.sheet.append_row(row_data)
                    added_count += 1
                    
                    logger.info(f"✅ Added: {article['title'][:60]}... (Score: {article['score']})")
                    logger.info(f"🎯 Keywords: {', '.join(article['matched_keywords'][:3])}")
                    
                    # Rate limiting to prevent API quota issues
                    time.sleep(2.0)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add article: {e}")
                    continue
                    
            logger.info(f"📊 Successfully added {added_count} articles to sheet")
            
        except Exception as e:
            logger.error(f"❌ Failed to add articles to sheet: {e}")
            raise
            
    def run_curation(self):
        """Main curation function - fetch, score, and add articles"""
        try:
            logger.info("🚀 Starting news curation run...")
            start_time = time.time()
            
            # Fetch and score articles
            articles = self.fetch_all_articles()
            
            if articles:
                logger.info(f"📊 Found {len(articles)} high-quality articles")
                
                # Log top articles for monitoring
                for i, article in enumerate(articles[:3], 1):
                    logger.info(f"#{i}: {article['title'][:50]}... (Score: {article['score']})")
                
                # Add to Google Sheets
                self.add_articles_to_sheet(articles)
                
                duration = time.time() - start_time
                logger.info(f"🎉 Curation completed successfully in {duration:.1f} seconds!")
                
            else:
                logger.info("📭 No articles met relevance threshold today")
                
        except Exception as e:
            logger.error(f"💥 Curation run failed: {e}")
            
    def cleanup_processed_articles(self):
        """Clean up old processed article IDs to prevent memory bloat"""
        # Keep only recent processed articles (last 1000)
        if len(self.processed_articles) > 1000:
            # Convert to list, keep last 500, convert back to set
            recent_articles = list(self.processed_articles)[-500:]
            self.processed_articles = set(recent_articles)
            logger.info("🧹 Cleaned up processed articles cache")

def main():
    """Main application loop for Render Background Worker"""
    try:
        logger.info("🤖 Atticus News Curator starting up...")
        
        # Initialize curator
        curator = AttticusNewsCurator()
        
        # Schedule curation runs
        # 9:00 AM EST
        schedule.every().day.at("14:00").do(curator.run_curation)  # 9 AM EST = 2 PM UTC
        # 3:00 PM EST  
        schedule.every().day.at("20:00").do(curator.run_curation)  # 3 PM EST = 8 PM UTC
        
        # Daily cleanup
        schedule.every().day.at("06:00").do(curator.cleanup_processed_articles)
        
        logger.info("⏰ Scheduled for 9:00 AM and 3:00 PM EST daily")
        
        # Run initial curation for testing
        logger.info("🧪 Running initial curation test...")
        curator.run_curation()
        
        logger.info("✅ Initial run completed. Starting scheduled loop...")
        
        # Main scheduling loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        raise

if __name__ == "__main__":
    main()
