#!/usr/bin/env python3
"""
Configuration file for Atticus News Curator
Modify these settings to customize the curator behavior
"""

# Keyword weights for article scoring
# Higher numbers = more important keywords
KEYWORD_WEIGHTS = {
    # Primary focus - Bitcoin/crypto options
    'bitcoin options': 15,
    'btc options': 15,
    'crypto options': 12,
    'defi options': 10,
    
    # Trading strategies and derivatives  
    'perpetual futures': 10,
    'crypto derivatives': 9,
    'options trading': 12,
    'volatility trading': 8,
    'derivatives market': 8,
    
    # Risk management and protection
    'downside protection': 8,
    'hedging strategies': 7,
    'portfolio protection': 7,
    'risk management': 6,
    'crypto hedge': 6,
    
    # Institutional and market structure
    'institutional crypto': 8,
    'institutional adoption': 7,
    'btc etf': 7,
    'trading infrastructure': 6,
    'market making': 7,
    'liquidity provision': 6,
    
    # General crypto and web3
    'web3': 5,
    'crypto volatility': 6,
    'digital assets': 4,
    'automated trading': 5,
    'algorithmic trading': 5
}

# RSS feeds to monitor
RSS_FEEDS = [
    'https://cointelegraph.com/rss',
    'https://decrypt.co/feed', 
    'https://blockworks.co/feed',
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://thedefiant.io/feed',
    'https://cryptonews.com/news/feed',
    'https://www.theblockcrypto.com/rss.xml',
    'https://bitcoinmagazine.com/.rss/full/'
]

# Scoring thresholds
MIN_RELEVANCE_SCORE = 8  # Minimum score for article inclusion
MAX_ARTICLES_PER_RUN = 5  # Maximum articles to add per curation run
SAMPLE_COPY_MAX_LENGTH = 140  # Maximum length for sample copy

# Timing configuration (UTC times)
MORNING_RUN_UTC = "14:00"  # 9 AM EST
AFTERNOON_RUN_UTC = "20:00"  # 3 PM EST
CLEANUP_TIME_UTC = "06:00"  # 1 AM EST

# Rate limiting (seconds between operations)
FEED_FETCH_DELAY = 1.0
SHEET_UPDATE_DELAY = 2.0

# Cache management
MAX_PROCESSED_ARTICLES = 1000
CLEANUP_THRESHOLD = 500
