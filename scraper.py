
# import asyncio
# import json
# from datetime import datetime
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
# from bs4 import BeautifulSoup
# from openai import OpenAI
# import re
# import gspread
# from google.oauth2.service_account import Credentials
# import os


# # Initialize Perplexity client from environment variable
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),  # Read from GitHub Secrets
#     base_url="https://api.perplexity.ai"
# )


# # Google Sheets Configuration
# GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"  # Created dynamically by GitHub Actions
# GOOGLE_SHEET_NAME = "Instagram Scripts"
# GOOGLE_WORKSHEET_NAME = "Scripts"


# # Track token usage (CORRECTED: $1 per 1M tokens)
# total_tokens_used = 0
# total_cost = 0.0


# def setup_google_sheets():
#     """
#     Initialize Google Sheets connection
#     """
#     try:
#         # Define the scope
#         scope = [
#             'https://spreadsheets.google.com/feeds',
#             'https://www.googleapis.com/auth/drive'
#         ]
        
#         # Load credentials
#         creds = Credentials.from_service_account_file(
#             GOOGLE_SHEETS_CREDENTIALS_FILE, 
#             scopes=scope
#         )
        
#         # Authorize and connect
#         client = gspread.authorize(creds)
        
#         # Open or create spreadsheet
#         try:
#             sheet = client.open(GOOGLE_SHEET_NAME)
#             print(f"✅ Connected to existing sheet: '{GOOGLE_SHEET_NAME}'")
#         except gspread.SpreadsheetNotFound:
#             sheet = client.create(GOOGLE_SHEET_NAME)
#             print(f"✅ Created new sheet: '{GOOGLE_SHEET_NAME}'")
        
#         # Open or create worksheet
#         try:
#             worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
#             print(f"✅ Using worksheet: '{GOOGLE_WORKSHEET_NAME}'")
#         except gspread.WorksheetNotFound:
#             worksheet = sheet.add_worksheet(
#                 title=GOOGLE_WORKSHEET_NAME,
#                 rows=1000,
#                 cols=10
#             )
#             # Add headers (only 4 columns now)
#             worksheet.update('A1:D1', [[
#                 'Timestamp',
#                 'Title',
#                 'Script',
#                 'Source Link'
#             ]])
            
#             # Format headers (bold, colored background, white text)
#             worksheet.format('A1:D1', {
#                 'textFormat': {
#                     'bold': True,
#                     'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}  # White text
#                 },
#                 'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},  # Blue background
#                 'horizontalAlignment': 'CENTER'
#             })
            
#             # Set column widths
#             worksheet.set_column_width('A', 180)  # Timestamp
#             worksheet.set_column_width('B', 400)  # Title
#             worksheet.set_column_width('C', 600)  # Script (wide)
#             worksheet.set_column_width('D', 400)  # Source Link
            
#             print(f"✅ Created new worksheet with headers: '{GOOGLE_WORKSHEET_NAME}'")
        
#         return worksheet
        
#     except FileNotFoundError:
#         print(f"❌ Error: '{GOOGLE_SHEETS_CREDENTIALS_FILE}' not found!")
#         print("💡 This file is created automatically by GitHub Actions")
#         return None
#     except Exception as e:
#         print(f"❌ Google Sheets setup error: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# def save_to_google_sheets(worksheet, script, source_link, news_title):
#     """
#     Append script data to Google Sheets with proper formatting
#     Only saves: Timestamp, Title, Script, Source Link
#     """
#     try:
#         # Get current timestamp
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
#         # Ensure all values are proper strings
#         if isinstance(script, list):
#             script = '\n'.join(str(item) for item in script)
#         else:
#             script = str(script).strip()
        
#         # Clean up any remaining brackets
#         script = script.replace('[', '').replace(']', '')
        
#         # Ensure other fields are strings
#         news_title = str(news_title).strip()
#         source_link = str(source_link).strip()
        
#         # Prepare row data (4 columns)
#         row_data = [
#             timestamp,
#             news_title,
#             script,
#             source_link
#         ]
        
#         # Get next row number
#         next_row = len(worksheet.get_all_values()) + 1
        
#         # Append to the sheet with RAW string values
#         worksheet.append_row(row_data, value_input_option='RAW')
        
#         # Format the newly added row (BLACK text, white background, wrap text)
#         row_range = f'A{next_row}:D{next_row}'
#         worksheet.format(row_range, {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })
        
#         # Format Script column (C) - wrap and left align
#         worksheet.format(f'C{next_row}', {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP',
#             'horizontalAlignment': 'LEFT'
#         })
        
#         # Format Title column (B) - left align
#         worksheet.format(f'B{next_row}', {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP',
#             'horizontalAlignment': 'LEFT'
#         })
        
#         # Format link column (D) - clickable blue
#         worksheet.format(f'D{next_row}', {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.06, 'green': 0.27, 'blue': 0.8},
#                 'fontSize': 10,
#                 'underline': True
#             },
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })
        
#         print(f"✅ Script saved to Google Sheets!")
#         print(f"   Row #{next_row} added with timestamp: {timestamp}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Error saving to Google Sheets: {e}")
#         import traceback
#         traceback.print_exc()
#         return False


# async def scrape_marathi_news_final():
#     """
#     Scraper that collects articles from all three sites
#     """
    
#     news_sites = [
#         {
#             "name": "TV9 Marathi",
#             "url": "https://www.tv9marathi.com/latest-news",
#             "article_selector": "article, div.story-card, div.news-item",
#             "link_pattern": "tv9marathi.com"
#         },
#         {
#             "name": "ABP Majha",
#             "url": "https://marathi.abplive.com/news",
#             "article_selector": "article, div.story-box, div.news-card",
#             "link_pattern": "abplive.com"
#         },
#         {
#             "name": "Lokmat",
#             "url": "https://www.lokmat.com/latestnews/",
#             "article_selector": "article, div.story-card, div.card-body",
#             "link_pattern": "lokmat.com"
#         }
#     ]
    
#     all_news = []
    
#     async with AsyncWebCrawler(verbose=True) as crawler:
        
#         for site in news_sites:
#             print(f"\n🔍 Scraping {site['name']}...")
            
#             try:
#                 # Fetch homepage with JavaScript rendering
#                 config = CrawlerRunConfig(
#                     cache_mode=CacheMode.BYPASS,
#                     wait_for="body",
#                     word_count_threshold=10,
#                     page_timeout=30000,
#                     js_code="""
#                     // Wait for content to load
#                     await new Promise(r => setTimeout(r, 2000));
#                     """
#                 )
                
#                 result = await crawler.arun(site['url'], config=config)
                
#                 if result.success:
#                     soup = BeautifulSoup(result.html, 'html.parser')
                    
#                     raw_articles = []
#                     all_links = soup.find_all('a', href=True)
                    
#                     for link_tag in all_links:
#                         href = link_tag.get('href', '')
#                         title = link_tag.get_text(strip=True)
                        
#                         # Filter valid news links
#                         if (len(title) > 15 and len(title) < 300 and
#                             site['link_pattern'] in href and
#                             not any(x in href for x in [
#                                 'javascript:', 'mailto:', '#', 
#                                 '/category/', '/tag/', '/author/',
#                                 'facebook.com', 'twitter.com', 'instagram.com',
#                                 'youtube.com', 'whatsapp.com', '/myaccount/',
#                                 '/install_app', '/advertisement', '/epaper',
#                                 'web-stories', 'photo-gallery', '/videos/',
#                                 '/sakhi/', '/astro/', '/bhakti/', '/games/',
#                                 '/jokes/', '/terms-and-conditions', '/utility-news',
#                                 '/spiritual-adhyatmik', '/rashi-bhavishya', 
#                                 '/topic/', '/elections/', '/career/'
#                             ])):
                            
#                             # Make absolute URL
#                             if href.startswith('/'):
#                                 base_url = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
#                                 href = base_url + href
                            
#                             if href.startswith('http'):
#                                 raw_articles.append({
#                                     'title': title,
#                                     'link': href
#                                 })
                    
#                     # Remove duplicates by link
#                     seen_links = set()
#                     unique_articles = []
#                     for article in raw_articles:
#                         if article['link'] not in seen_links:
#                             unique_articles.append(article)
#                             seen_links.add(article['link'])
                    
#                     print(f"📋 Found {len(unique_articles)} unique articles from {site['name']}")
                    
#                     if len(unique_articles) > 0:
#                         print(f"📄 Fetching detailed content from top {min(12, len(unique_articles))} articles...")
                        
#                         articles_with_content = []
#                         for article in unique_articles[:12]:
#                             try:
#                                 article_result = await crawler.arun(
#                                     article['link'],
#                                     config=CrawlerRunConfig(
#                                         cache_mode=CacheMode.BYPASS,
#                                         word_count_threshold=50,
#                                         page_timeout=15000
#                                     )
#                                 )
                                
#                                 if article_result.success and len(article_result.markdown) > 100:
#                                     articles_with_content.append({
#                                         'title': article['title'],
#                                         'link': article['link'],
#                                         'content': article_result.markdown[:2500]
#                                     })
#                                     print(f"   ✓ {article['title'][:60]}...")
                                    
#                             except Exception as e:
#                                 continue
                        
#                         print(f"✅ Fetched content for {len(articles_with_content)} articles")
                        
#                         # AI analysis
#                         if articles_with_content:
#                             filtered_news = await smart_analyze_with_detailed_summary(
#                                 articles_with_content, 
#                                 site['name']
#                             )
#                             all_news.extend(filtered_news)
#                             print(f"✅ Extracted {len(filtered_news)} important articles")
#                     else:
#                         print(f"⚠️ No articles found from {site['name']}")
                
#                 else:
#                     print(f"❌ Failed to fetch {site['name']}: {result.error_message}")
                    
#             except Exception as e:
#                 print(f"❌ Error scraping {site['name']}: {e}")
#                 import traceback
#                 traceback.print_exc()
    
#     return all_news


# async def smart_analyze_with_detailed_summary(articles, source_name):
#     """
#     AI analysis with token tracking ($1 per 1M tokens)
#     """
#     global total_tokens_used, total_cost
    
#     print(f"\n🧠 Using AI for detailed analysis of {source_name} articles...")
    
#     all_filtered = []
    
#     # Process in batches of 5
#     for i in range(0, len(articles), 5):
#         batch = articles[i:i+5]
        
#         articles_text = ""
#         for idx, article in enumerate(batch, i+1):
#             articles_text += f"""
# बातमी #{idx}:
# शीर्षक: {article['title']}
# Link: {article['link']}
# Content: {article['content'][:1200]}

# ---
# """
        
#         prompt = f"""
# तुम्ही एक तज्ञ मराठी बातम्या विश्लेषक आहात. खालील बातम्यांचे विश्लेषण करा.

# **फक्त हे प्रकार निवडा:**
# 1. गुन्हेगारी बातम्या (Crime) - हत्या, दरोडा, अपघात, अटक, लाच
# 2. राजकीय बातम्या (Political) - निवडणुका, सरकार, महापालिका, राजकीय घडामोडी
# 3. महत्त्वाच्या सामान्य बातम्या (Important General) - शासकीय निर्णय, सामाजिक मुद्दे

# **टाळावे:** मनोरंजन gossip, ज्योतिष, फॅशन, lifestyle, खेळाची सामान्य बातमी, job posts, धार्मिक कथा, Bigg Boss, बॉलीवूड gossip

# **JSON format (फक्त array परत करा):**
# [
#   {{
#     "title": "मूळ शीर्षक",
#     "category": "crime/politics/general",
#     "detailed_summary": "संपूर्ण विस्तृत सारांश 150-250 शब्दांत मराठीत",
#     "importance": "high/medium/low",
#     "link": "URL",
#     "article_number": number,
#     "key_points": ["मुद्दा 1", "मुद्दा 2", "मुद्दा 3"]
#   }}
# ]

# {articles_text}
# """
        
#         try:
#             response = perplexity_client.chat.completions.create(
#                 model="sonar-pro",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert Marathi news analyst. Return ONLY valid JSON array."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.3,
#                 max_tokens=4000
#             )
            
#             # Track tokens
#             if hasattr(response, 'usage'):
#                 batch_tokens = response.usage.total_tokens
#                 total_tokens_used += batch_tokens
#                 batch_cost = (batch_tokens / 1_000_000) * 1.0
#                 total_cost += batch_cost
#                 print(f"   📊 Batch tokens: {batch_tokens:,} | Cost: ${batch_cost:.4f}")
            
#             content = response.choices[0].message.content
#             json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
#             if json_match:
#                 batch_articles = json.loads(json_match.group())
#                 all_filtered.extend(batch_articles)
#                 print(f"   ✅ Extracted {len(batch_articles)} articles")
            
#         except Exception as e:
#             print(f"   ❌ AI analysis error: {e}")
    
#     # Add source and timestamp
#     for article in all_filtered:
#         article['source'] = source_name
#         article['scraped_at'] = datetime.now().isoformat()
    
#     return all_filtered


# def create_reel_script(news_articles):
#     """
#     Generate Instagram Reel script from news articles
#     Returns: (script, source_link, news_title)
#     """
#     global total_tokens_used, total_cost
    
#     # Prepare news context
#     news_context = ""
#     for idx, article in enumerate(news_articles[:5], 1):
#         news_context += f"""
# बातमी #{idx}:
# शीर्षक: {article['title']}
# प्रकार: {article['category']}
# सारांश: {article['detailed_summary']}
# महत्त्व: {article['importance']}
# लिंक: {article['link']}
# ---
# """
    
#     # System prompt with diverse hook examples
#     system_prompt = """
# तुम्ही "जबरी खबरी" Instagram Reels चे एक्सपर्ट स्क्रिप्ट रायटर आहात.

# **HOOK VARIETY (पहिल्या 2 ओळी):**
# 1. Shock Statement: "एका अपघाताने संपूर्ण राज्य हादरलं."
# 2. Direct Question: "तुम्हाला माहिती आहे का...?"
# 3. Breaking News: "नुकतीच एक धक्कादायक माहिती समोर आली."
# 4. Name Drop: "[व्यक्ती नाव] आज चर्चेत का आहे?"
# 5. Contrast/Twist: "दिसतं काहीतरी, पण वास्तव वेगळंच."

# **स्ट्रक्चर (40-60 seconds):**
# - पहिले 2 ओळी: Hook (वेगळी style)
# - 3-10 ओळी: मुख्य घटना
# - 11-14 ओळी: ट्विस्ट/प्रश्न
# - शेवटच्या 2-3 ओळी: CTA

# **ENDING:**
# "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

# **OUTPUT:** फक्त स्क्रिप्ट. 15-18 ओळी. शेवटी: ---ARTICLE_NUMBER: X---
# """
    
#     user_prompt = f"""
# खालील बातम्यांपैकी सर्वात ENGAGING बातमी निवडून Instagram Reel script तयार करा.

# **आजच्या बातम्या:**
# {news_context}

# **तुमचं काम:**
# 1. सर्वात STRONG बातमी निवडा
# 2. योग्य hook style वापरा
# 3. 15-18 ओळींची script लिहा
# 4. शेवटी article number द्या

# OUTPUT: [स्क्रिप्ट]\n\n---ARTICLE_NUMBER: X---
# """
    
#     try:
#         response = perplexity_client.chat.completions.create(
#             model="sonar-pro",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.8,
#             max_tokens=1500
#         )
        
#         # Track tokens
#         if hasattr(response, 'usage'):
#             script_tokens = response.usage.total_tokens
#             total_tokens_used += script_tokens
#             total_cost += (script_tokens / 1_000_000) * 1.0
        
#         full_response = response.choices[0].message.content.strip()
        
#         # Extract script and article number
#         if "---ARTICLE_NUMBER:" in full_response:
#             parts = full_response.split("---ARTICLE_NUMBER:")
#             script = parts[0].strip()
#             article_num_str = parts[1].strip().replace("---", "").strip()
#             try:
#                 article_num = int(article_num_str) - 1
#             except:
#                 article_num = 0
#         else:
#             script = full_response
#             article_num = 0
        
#         # Clean up
#         script = script.replace('```', '').strip()
#         script = script.replace('---ARTICLE_NUMBER:', '').strip()
        
#         # Get source article
#         if article_num < len(news_articles):
#             source_article = news_articles[article_num]
#         else:
#             source_article = news_articles
        
#         source_link = source_article.get('link', 'N/A')
#         news_title = source_article.get('title', 'N/A')
        
#         return script, source_link, news_title
        
#     except Exception as e:
#         print(f"❌ Error generating script: {e}")
#         return None, None, None


# async def main():
#     global total_tokens_used, total_cost
    
#     print("🚀 Starting Smart Marathi News Scraper + Script Generator")
#     print("📍 Focus: Criminal, Political & Important General News")
#     print("📝 Feature: Detailed summaries + Instagram Scripts")
#     print("💰 Token tracking enabled")
#     print("📊 Output: Direct to Google Sheets\n")
    
#     start_time = datetime.now()
    
#     # PART 1: SCRAPING
#     all_articles = await scrape_marathi_news_final()
    
#     # Remove duplicates
#     unique_articles = []
#     seen_titles = set()
    
#     for article in all_articles:
#         title_lower = article['title'].lower()
#         if title_lower not in seen_titles:
#             unique_articles.append(article)
#             seen_titles.add(title_lower)
    
#     # Sort by importance
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     unique_articles.sort(key=lambda x: priority_order.get(x.get('importance', 'medium'), 2))
    
#     top_10_articles = unique_articles[:10]
    
#     end_scrape = datetime.now()
#     scrape_duration = (end_scrape - start_time).total_seconds()
    
#     # Scraping summary
#     print("\n" + "="*80)
#     print("📊 SCRAPING SUMMARY")
#     print("="*80)
#     print(f"   Total articles: {len(unique_articles)}")
#     print(f"   High importance: {len([a for a in unique_articles if a.get('importance') == 'high'])}")
#     print(f"   Crime: {len([a for a in unique_articles if a.get('category') == 'crime'])}")
#     print(f"   Political: {len([a for a in unique_articles if a.get('category') == 'politics'])}")
#     print(f"   General: {len([a for a in unique_articles if a.get('category') == 'general'])}")
#     print(f"\n⏱️  Scraping time: {scrape_duration:.2f} seconds")
#     print("="*80 + "\n")
    
#     # PART 2: SCRIPT GENERATION
#     print("="*80)
#     print("🎬 GENERATING INSTAGRAM SCRIPT")
#     print("="*80 + "\n")
    
#     worksheet = setup_google_sheets()
    
#     if worksheet and len(top_10_articles) > 0:
#         print(f"\n🎯 Generating script from TOP 10 articles...\n")
        
#         script, source_link, news_title = create_reel_script(top_10_articles)
        
#         if script:
#             print("\n" + "="*70)
#             print("📝 GENERATED SCRIPT:")
#             print("="*70)
#             print(script)
#             print("\n" + "="*70)
#             print(f"📰 Title: {news_title}")
#             print(f"🔗 Source: {source_link}")
#             print("="*70 + "\n")
            
#             success = save_to_google_sheets(worksheet, script, source_link, news_title)
            
#             if success:
#                 print(f"📈 View sheet: https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")
#         else:
#             print("❌ Failed to generate script")
#     else:
#         print("⚠️ No articles or Google Sheets unavailable")
    
#     end_time = datetime.now()
#     total_duration = (end_time - start_time).total_seconds()
    
#     # Final summary
#     print("\n" + "="*80)
#     print("✅ COMPLETE!")
#     print("="*80)
#     print(f"   Total articles: {len(unique_articles)}")
#     print(f"   Scripts generated: 1")
#     print(f"   Saved to: {GOOGLE_SHEET_NAME}")
#     print(f"\n   ⏱️ Total time: {total_duration:.2f} seconds")
#     print(f"   🔢 Total tokens: {total_tokens_used:,}")
#     print(f"   💰 Total cost: ${total_cost:.4f}")
#     print("="*80 + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())




import asyncio
import json
from datetime import datetime, date
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import gspread
from google.oauth2.service_account import Credentials
import os
from typing import List, Dict
import hashlib


# Initialize Perplexity client from environment variable
perplexity_client = OpenAI(
    api_key=os.environ.get("PERPLEXITY_API_KEY"),  # Read from GitHub Secrets
    base_url="https://api.perplexity.ai"
)


# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"  # Created by GitHub Actions
GOOGLE_SHEET_NAME = "Instagram Scripts"
GOOGLE_WORKSHEET_NAME = "Scripts"


# Categories
VALID_CATEGORIES = [
    "sports", "general", "crime", "politics", 
    "education", "economy", "entertainment", "horror"
]


# Track token usage and costs
total_tokens_used = 0
total_cost = 0.0
processed_hashes = set()  # To avoid duplicate news


def setup_google_sheets():
    """Initialize Google Sheets connection"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE, 
            scopes=scope
        )
        
        client = gspread.authorize(creds)
        
        try:
            sheet = client.open(GOOGLE_SHEET_NAME)
            print(f"✅ Connected to existing sheet: '{GOOGLE_SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(GOOGLE_SHEET_NAME)
            print(f"✅ Created new sheet: '{GOOGLE_SHEET_NAME}'")
        
        try:
            worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
            print(f"✅ Using worksheet: '{GOOGLE_WORKSHEET_NAME}'")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(
                title=GOOGLE_WORKSHEET_NAME,
                rows=2000,
                cols=10
            )
            # Add headers (5 columns: Timestamp, Category, Title, Script, Source Link)
            worksheet.update('A1:E1', [[
                'Timestamp',
                'Category',
                'Title',
                'Script',
                'Source Link'
            ]])
            
            # Format headers
            worksheet.format('A1:E1', {
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                },
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'horizontalAlignment': 'CENTER'
            })
            
            # Set column widths
            worksheet.set_column_width('A', 180)   # Timestamp
            worksheet.set_column_width('B', 150)   # Category
            worksheet.set_column_width('C', 400)   # Title
            worksheet.set_column_width('D', 600)   # Script
            worksheet.set_column_width('E', 400)   # Source Link
            
            print(f"✅ Created new worksheet with headers")
        
        return worksheet
        
    except FileNotFoundError:
        print(f"❌ Error: '{GOOGLE_SHEETS_CREDENTIALS_FILE}' not found!")
        print("💡 This file is created automatically by GitHub Actions")
        return None
    except Exception as e:
        print(f"❌ Google Sheets setup error: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_to_google_sheets(worksheet, category, title, script, source_link):
    """Save script to Google Sheets with category"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean data
        if isinstance(script, list):
            script = '\n'.join(str(item) for item in script)
        else:
            script = str(script).strip()
        
        script = script.replace('[', '').replace(']', '')
        title = str(title).strip()
        source_link = str(source_link).strip()
        category = str(category).strip().lower()
        
        # Validate category
        if category not in VALID_CATEGORIES:
            category = "general"
        
        row_data = [timestamp, category, title, script, source_link]
        
        next_row = len(worksheet.get_all_values()) + 1
        worksheet.append_row(row_data, value_input_option='RAW')
        
        # Format the row
        row_range = f'A{next_row}:E{next_row}'
        worksheet.format(row_range, {
            'textFormat': {
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
                'fontSize': 10
            },
            'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP'
        })
        
        # Format category column with color coding
        category_colors = {
            'crime': {'red': 0.95, 'green': 0.8, 'blue': 0.8},
            'politics': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
            'sports': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
            'entertainment': {'red': 1.0, 'green': 0.9, 'blue': 0.8},
            'education': {'red': 0.9, 'green': 0.95, 'blue': 1.0},
            'economy': {'red': 0.95, 'green': 1.0, 'blue': 0.85},
            'horror': {'red': 0.7, 'green': 0.7, 'blue': 0.7},
            'general': {'red': 1.0, 'green': 1.0, 'blue': 0.9}
        }
        
        worksheet.format(f'B{next_row}', {
            'textFormat': {
                'bold': True,
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
                'fontSize': 10
            },
            'backgroundColor': category_colors.get(category, category_colors['general']),
            'horizontalAlignment': 'CENTER'
        })
        
        print(f"✅ Saved [{category.upper()}] {title[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to Google Sheets: {e}")
        return False


def get_content_hash(title: str, content: str) -> str:
    """Generate hash to detect duplicate news"""
    combined = f"{title.lower()}{content[:200].lower()}"
    return hashlib.md5(combined.encode()).hexdigest()


async def scrape_multiple_marathi_sources():
    """Scrape from multiple trusted Marathi news sources"""
    
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
    news_sites = [
        {
            "name": "TV9 Marathi",
            "url": "https://www.tv9marathi.com/latest-news",
            "article_selector": "article, div.story-card",
            "link_pattern": "tv9marathi.com",
            "target": 10
        },
        {
            "name": "ABP Majha",
            "url": "https://marathi.abplive.com/news",
            "article_selector": "article, div.story-box",
            "link_pattern": "abplive.com",
            "target": 10
        },
        {
            "name": "Lokmat",
            "url": "https://www.lokmat.com/latestnews/",
            "article_selector": "article, div.story-card",
            "link_pattern": "lokmat.com",
            "target": 10
        },
        {
            "name": "Maharashtra Times",
            "url": "https://maharashtratimes.com/",
            "article_selector": "article, div.brief-story",
            "link_pattern": "maharashtratimes.com",
            "target": 8
        },
        {
            "name": "NDTV Marathi",
            "url": "https://marathi.ndtv.com/",
            "article_selector": "article, div.news_Itm",
            "link_pattern": "marathi.ndtv.com",
            "target": 8
        },
        {
            "name": "Zee 24 Taas",
            "url": "https://zeenews.india.com/marathi/",
            "article_selector": "article, div.story",
            "link_pattern": "zeenews.india.com/marathi",
            "target": 8
        },
        {
            "name": "Loksatta",
            "url": "https://www.loksatta.com/",
            "article_selector": "article, div.item",
            "link_pattern": "loksatta.com",
            "target": 6
        }
    ]
    
    all_news = []
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        
        for site in news_sites:
            print(f"\n🔍 Scraping {site['name']}...")
            
            try:
                config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    wait_for="body",
                    word_count_threshold=10,
                    page_timeout=30000,
                    js_code="await new Promise(r => setTimeout(r, 2000));"
                )
                
                result = await crawler.arun(site['url'], config=config)
                
                if result.success:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    raw_articles = []
                    all_links = soup.find_all('a', href=True)
                    
                    for link_tag in all_links:
                        href = link_tag.get('href', '')
                        title = link_tag.get_text(strip=True)
                        
                        if (len(title) > 15 and len(title) < 300 and
                            site['link_pattern'] in href and
                            not any(x in href.lower() for x in [
                                'javascript:', 'mailto:', '#', 
                                '/category/', '/tag/', '/author/',
                                'facebook.com', 'twitter.com', 'instagram.com',
                                'youtube.com', 'whatsapp.com', '/myaccount/',
                                '/install_app', '/advertisement', '/epaper',
                                'web-stories', 'photo-gallery', '/videos/',
                                '/games/', '/jokes/', '/terms-and-conditions',
                                '/topic/', '/widget/'
                            ])):
                            
                            if href.startswith('/'):
                                base_url = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
                                href = base_url + href
                            
                            if href.startswith('http'):
                                raw_articles.append({
                                    'title': title,
                                    'link': href
                                })
                    
                    # Remove duplicates
                    seen_links = set()
                    unique_articles = []
                    for article in raw_articles:
                        if article['link'] not in seen_links:
                            unique_articles.append(article)
                            seen_links.add(article['link'])
                    
                    print(f"📋 Found {len(unique_articles)} unique articles")
                    
                    if len(unique_articles) > 0:
                        articles_with_content = []
                        
                        for article in unique_articles[:site['target']]:
                            try:
                                article_result = await crawler.arun(
                                    article['link'],
                                    config=CrawlerRunConfig(
                                        cache_mode=CacheMode.BYPASS,
                                        word_count_threshold=50,
                                        page_timeout=15000
                                    )
                                )
                                
                                if article_result.success and len(article_result.markdown) > 100:
                                    content_hash = get_content_hash(article['title'], article_result.markdown)
                                    
                                    if content_hash not in processed_hashes:
                                        articles_with_content.append({
                                            'title': article['title'],
                                            'link': article['link'],
                                            'content': article_result.markdown[:2500],
                                            'hash': content_hash
                                        })
                                        processed_hashes.add(content_hash)
                                        print(f"   ✓ {article['title'][:60]}...")
                                    
                            except Exception as e:
                                continue
                        
                        print(f"✅ Fetched {len(articles_with_content)} articles")
                        
                        if articles_with_content:
                            filtered_news = await smart_analyze_with_category(
                                articles_with_content, 
                                site['name']
                            )
                            all_news.extend(filtered_news)
                
                else:
                    print(f"❌ Failed to fetch {site['name']}")
                    
            except Exception as e:
                print(f"❌ Error scraping {site['name']}: {e}")
            
            await asyncio.sleep(2)
    
    return all_news


async def smart_analyze_with_category(articles: List[Dict], source_name: str):
    """AI analysis with proper categorization"""
    global total_tokens_used, total_cost
    
    print(f"\n🧠 Analyzing {source_name} articles...")
    
    all_filtered = []
    
    for i in range(0, len(articles), 3):
        batch = articles[i:i+3]
        
        articles_text = ""
        for idx, article in enumerate(batch, i+1):
            articles_text += f"""
बातमी #{idx}:
शीर्षक: {article['title']}
Link: {article['link']}
Content: {article['content'][:1200]}

---
"""
        
        prompt = f"""
तुम्ही एक तज्ञ मराठी बातम्या विश्लेषक आहात. खालील बातम्यांचे विश्लेषण करा आणि प्रत्येक बातमीला योग्य category द्या.

**Categories (फक्त यापैकी एक निवडा):**
1. sports - क्रीडा बातम्या
2. general - सामान्य महत्त्वाच्या बातम्या
3. crime - गुन्हेगारी बातम्या
4. politics - राजकीय बातम्या
5. education - शैक्षणिक बातम्या
6. economy - आर्थिक/व्यवसाय बातम्या
7. entertainment - मनोरंजन बातम्या
8. horror - भयानक/दुःखद घटना

**JSON format:**
[
  {{
    "title": "मूळ शीर्षक",
    "category": "category name",
    "detailed_summary": "विस्तृत सारांश 150-250 शब्दांत",
    "importance": "high/medium/low",
    "link": "URL",
    "article_number": number,
    "key_points": ["मुद्दा 1", "मुद्दा 2", "मुद्दा 3"]
  }}
]

{articles_text}
"""
        
        try:
            response = perplexity_client.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Marathi news analyst. Return ONLY valid JSON array."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            if hasattr(response, 'usage'):
                batch_tokens = response.usage.total_tokens
                total_tokens_used += batch_tokens
                batch_cost = (batch_tokens / 1_000_000) * 1.0
                total_cost += batch_cost
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                batch_articles = json.loads(json_match.group())
                all_filtered.extend(batch_articles)
                print(f"   ✅ Extracted {len(batch_articles)} articles")
            
        except Exception as e:
            print(f"   ❌ AI analysis error: {e}")
        
        await asyncio.sleep(1)
    
    for article in all_filtered:
        article['source'] = source_name
        article['scraped_at'] = datetime.now().isoformat()
    
    return all_filtered


async def create_reel_script_single(news_article: Dict):
    """Generate Instagram Reel script for a SINGLE news article"""
    global total_tokens_used, total_cost
    
    category = news_article.get('category', 'general')
    
    system_prompt = """
तुम्ही "जबरी खबरी" Instagram Reels चे एक्सपर्ट स्क्रिप्ट रायटर आहात.

**HOOK VARIETY (पहिल्या 2 ओळी):**
1. Shock Statement: "एका अपघाताने संपूर्ण राज्य हादरलं."
2. Direct Question: "तुम्हाला माहिती आहे का...?"
3. Breaking News: "नुकतीच एक धक्कादायक माहिती समोर आली."
4. Name Drop: "[व्यक्ती नाव] आज चर्चेत का आहे?"
5. Contrast/Twist: "दिसतं काहीतरी, पण वास्तव वेगळंच."

**स्ट्रक्चर (15-18 ओळी):**
- पहिले 2 ओळी: Hook
- 3-10 ओळी: मुख्य घटना
- 11-14 ओळी: ट्विस्ट/प्रश्न
- शेवटच्या 2-3 ओळी: CTA

**ENDING:**
"तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

OUTPUT: फक्त स्क्रिप्ट, 15-18 ओळी
"""
    
    user_prompt = f"""
खालील बातमीवर Instagram Reel script तयार करा.

**बातमी:**
शीर्षक: {news_article['title']}
Category: {category}
सारांश: {news_article['detailed_summary']}
मुद्दे: {', '.join(news_article.get('key_points', []))}

फक्त स्क्रिप्ट द्या, 15-18 ओळी.
"""
    
    try:
        response = perplexity_client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        if hasattr(response, 'usage'):
            script_tokens = response.usage.total_tokens
            total_tokens_used += script_tokens
            total_cost += (script_tokens / 1_000_000) * 1.0
        
        script = response.choices[0].message.content.strip()
        script = script.replace('```', '').strip()
        
        return script
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return None


async def main():
    global total_tokens_used, total_cost
    
    print("="*80)
    print("🚀 SMART MARATHI NEWS SCRAPER + SCRIPT GENERATOR v2.0")
    print("="*80)
    print("📍 Target: 50+ different news articles")
    print("📋 Categories: Sports, General, Crime, Politics, Education, Economy, Entertainment, Horror")
    print("🎬 Output: Individual scripts for each news")
    print("💾 Storage: Google Sheets with category column")
    print("="*80 + "\n")
    
    start_time = datetime.now()
    
    # STEP 1: SCRAPING
    print("\n" + "="*80)
    print("STEP 1: SCRAPING NEWS FROM MULTIPLE SOURCES")
    print("="*80 + "\n")
    
    all_articles = await scrape_multiple_marathi_sources()
    
    # Remove duplicates
    unique_articles = []
    seen_hashes = set()
    
    for article in all_articles:
        article_hash = article.get('hash', get_content_hash(article['title'], article.get('detailed_summary', '')))
        if article_hash not in seen_hashes:
            unique_articles.append(article)
            seen_hashes.add(article_hash)
    
    print(f"\n✅ Total unique articles: {len(unique_articles)}")
    
    # Category breakdown
    category_counts = {}
    for article in unique_articles:
        cat = article.get('category', 'general')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\n📊 Category Breakdown:")
    for cat, count in sorted(category_counts.items()):
        print(f"   {cat.upper()}: {count}")
    
    # Select top 50 articles
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    unique_articles.sort(key=lambda x: priority_order.get(x.get('importance', 'medium'), 2))
    
    selected_articles = unique_articles[:50]
    
    print(f"\n🎯 Selected {len(selected_articles)} articles for scripts")
    
    end_scrape = datetime.now()
    scrape_duration = (end_scrape - start_time).total_seconds()
    print(f"⏱️  Scraping: {scrape_duration:.2f} seconds\n")
    
    # STEP 2: SCRIPT GENERATION
    print("="*80)
    print("STEP 2: GENERATING SCRIPTS & SAVING TO GOOGLE SHEETS")
    print("="*80 + "\n")
    
    worksheet = setup_google_sheets()
    
    if worksheet and len(selected_articles) > 0:
        successful_saves = 0
        failed_saves = 0
        
        for idx, article in enumerate(selected_articles, 1):
            print(f"\n[{idx}/{len(selected_articles)}] {article['title'][:60]}...")
            
            script = await create_reel_script_single(article)
            
            if script:
                success = save_to_google_sheets(
                    worksheet,
                    article.get('category', 'general'),
                    article['title'],
                    script,
                    article['link']
                )
                
                if success:
                    successful_saves += 1
                else:
                    failed_saves += 1
            else:
                failed_saves += 1
            
            await asyncio.sleep(1.5)
        
        print("\n" + "="*80)
        print("✅ COMPLETE!")
        print("="*80)
        print(f"   Successfully saved: {successful_saves}")
        print(f"   Failed: {failed_saves}")
        print(f"   📊 View: https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")
    else:
        print("⚠️ No articles or Google Sheets unavailable")
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("📈 SUMMARY")
    print("="*80)
    print(f"   Articles scraped: {len(unique_articles)}")
    print(f"   Scripts generated: {successful_saves}")
    print(f"   Time: {total_duration:.2f} seconds")
    print(f"   Tokens: {total_tokens_used:,}")
    print(f"   Cost: ${total_cost:.4f}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
