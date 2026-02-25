
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




# import asyncio
# import json
# from datetime import datetime, date
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
# from bs4 import BeautifulSoup
# from openai import OpenAI
# import re
# import gspread
# from google.oauth2.service_account import Credentials
# import os
# from typing import List, Dict
# import hashlib


# # Initialize Perplexity client from environment variable
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),  # Read from GitHub Secrets
#     base_url="https://api.perplexity.ai"
# )


# # Google Sheets Configuration
# GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"  # Created by GitHub Actions
# GOOGLE_SHEET_NAME = "Instagram Scripts"
# GOOGLE_WORKSHEET_NAME = "Scripts"


# # Categories
# VALID_CATEGORIES = [
#     "sports", "general", "crime", "politics", 
#     "education", "economy", "entertainment", "horror"
# ]


# # Track token usage and costs
# total_tokens_used = 0
# total_cost = 0.0
# processed_hashes = set()  # To avoid duplicate news


# def setup_google_sheets():
#     """Initialize Google Sheets connection"""
#     try:
#         scope = [
#             'https://spreadsheets.google.com/feeds',
#             'https://www.googleapis.com/auth/drive'
#         ]
        
#         creds = Credentials.from_service_account_file(
#             GOOGLE_SHEETS_CREDENTIALS_FILE, 
#             scopes=scope
#         )
        
#         client = gspread.authorize(creds)
        
#         try:
#             sheet = client.open(GOOGLE_SHEET_NAME)
#             print(f"✅ Connected to existing sheet: '{GOOGLE_SHEET_NAME}'")
#         except gspread.SpreadsheetNotFound:
#             sheet = client.create(GOOGLE_SHEET_NAME)
#             print(f"✅ Created new sheet: '{GOOGLE_SHEET_NAME}'")
        
#         try:
#             worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
#             print(f"✅ Using worksheet: '{GOOGLE_WORKSHEET_NAME}'")
#         except gspread.WorksheetNotFound:
#             worksheet = sheet.add_worksheet(
#                 title=GOOGLE_WORKSHEET_NAME,
#                 rows=2000,
#                 cols=10
#             )
#             # Add headers (5 columns: Timestamp, Category, Title, Script, Source Link)
#             worksheet.update('A1:E1', [[
#                 'Timestamp',
#                 'Category',
#                 'Title',
#                 'Script',
#                 'Source Link'
#             ]])
            
#             # Format headers
#             worksheet.format('A1:E1', {
#                 'textFormat': {
#                     'bold': True,
#                     'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
#                 },
#                 'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
#                 'horizontalAlignment': 'CENTER'
#             })
            
#             # Set column widths
#             worksheet.set_column_width('A', 180)   # Timestamp
#             worksheet.set_column_width('B', 150)   # Category
#             worksheet.set_column_width('C', 400)   # Title
#             worksheet.set_column_width('D', 600)   # Script
#             worksheet.set_column_width('E', 400)   # Source Link
            
#             print(f"✅ Created new worksheet with headers")
        
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


# def save_to_google_sheets(worksheet, category, title, script, source_link):
#     """Save script to Google Sheets with category"""
#     try:
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
#         # Clean data
#         if isinstance(script, list):
#             script = '\n'.join(str(item) for item in script)
#         else:
#             script = str(script).strip()
        
#         script = script.replace('[', '').replace(']', '')
#         title = str(title).strip()
#         source_link = str(source_link).strip()
#         category = str(category).strip().lower()
        
#         # Validate category
#         if category not in VALID_CATEGORIES:
#             category = "general"
        
#         row_data = [timestamp, category, title, script, source_link]
        
#         next_row = len(worksheet.get_all_values()) + 1
#         worksheet.append_row(row_data, value_input_option='RAW')
        
#         # Format the row
#         row_range = f'A{next_row}:E{next_row}'
#         worksheet.format(row_range, {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })
        
#         # Format category column with color coding
#         category_colors = {
#             'crime': {'red': 0.95, 'green': 0.8, 'blue': 0.8},
#             'politics': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
#             'sports': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
#             'entertainment': {'red': 1.0, 'green': 0.9, 'blue': 0.8},
#             'education': {'red': 0.9, 'green': 0.95, 'blue': 1.0},
#             'economy': {'red': 0.95, 'green': 1.0, 'blue': 0.85},
#             'horror': {'red': 0.7, 'green': 0.7, 'blue': 0.7},
#             'general': {'red': 1.0, 'green': 1.0, 'blue': 0.9}
#         }
        
#         worksheet.format(f'B{next_row}', {
#             'textFormat': {
#                 'bold': True,
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': category_colors.get(category, category_colors['general']),
#             'horizontalAlignment': 'CENTER'
#         })
        
#         print(f"✅ Saved [{category.upper()}] {title[:50]}...")
#         return True
        
#     except Exception as e:
#         print(f"❌ Error saving to Google Sheets: {e}")
#         return False


# def get_content_hash(title: str, content: str) -> str:
#     """Generate hash to detect duplicate news"""
#     combined = f"{title.lower()}{content[:200].lower()}"
#     return hashlib.md5(combined.encode()).hexdigest()


# async def scrape_multiple_marathi_sources():
#     """Scrape from multiple trusted Marathi news sources"""
    
#     today = date.today()
#     today_str = today.strftime('%Y-%m-%d')
    
#     news_sites = [
#         {
#             "name": "TV9 Marathi",
#             "url": "https://www.tv9marathi.com/latest-news",
#             "article_selector": "article, div.story-card",
#             "link_pattern": "tv9marathi.com",
#             "target": 10
#         },
#         {
#             "name": "ABP Majha",
#             "url": "https://marathi.abplive.com/news",
#             "article_selector": "article, div.story-box",
#             "link_pattern": "abplive.com",
#             "target": 10
#         },
#         {
#             "name": "Lokmat",
#             "url": "https://www.lokmat.com/latestnews/",
#             "article_selector": "article, div.story-card",
#             "link_pattern": "lokmat.com",
#             "target": 10
#         },
#         {
#             "name": "Maharashtra Times",
#             "url": "https://maharashtratimes.com/",
#             "article_selector": "article, div.brief-story",
#             "link_pattern": "maharashtratimes.com",
#             "target": 8
#         },
#         {
#             "name": "NDTV Marathi",
#             "url": "https://marathi.ndtv.com/",
#             "article_selector": "article, div.news_Itm",
#             "link_pattern": "marathi.ndtv.com",
#             "target": 8
#         },
#         {
#             "name": "Zee 24 Taas",
#             "url": "https://zeenews.india.com/marathi/",
#             "article_selector": "article, div.story",
#             "link_pattern": "zeenews.india.com/marathi",
#             "target": 8
#         },
#         {
#             "name": "Loksatta",
#             "url": "https://www.loksatta.com/",
#             "article_selector": "article, div.item",
#             "link_pattern": "loksatta.com",
#             "target": 6
#         }
#     ]
    
#     all_news = []
    
#     async with AsyncWebCrawler(verbose=False) as crawler:
        
#         for site in news_sites:
#             print(f"\n🔍 Scraping {site['name']}...")
            
#             try:
#                 config = CrawlerRunConfig(
#                     cache_mode=CacheMode.BYPASS,
#                     wait_for="body",
#                     word_count_threshold=10,
#                     page_timeout=30000,
#                     js_code="await new Promise(r => setTimeout(r, 2000));"
#                 )
                
#                 result = await crawler.arun(site['url'], config=config)
                
#                 if result.success:
#                     soup = BeautifulSoup(result.html, 'html.parser')
                    
#                     raw_articles = []
#                     all_links = soup.find_all('a', href=True)
                    
#                     for link_tag in all_links:
#                         href = link_tag.get('href', '')
#                         title = link_tag.get_text(strip=True)
                        
#                         if (len(title) > 15 and len(title) < 300 and
#                             site['link_pattern'] in href and
#                             not any(x in href.lower() for x in [
#                                 'javascript:', 'mailto:', '#', 
#                                 '/category/', '/tag/', '/author/',
#                                 'facebook.com', 'twitter.com', 'instagram.com',
#                                 'youtube.com', 'whatsapp.com', '/myaccount/',
#                                 '/install_app', '/advertisement', '/epaper',
#                                 'web-stories', 'photo-gallery', '/videos/',
#                                 '/games/', '/jokes/', '/terms-and-conditions',
#                                 '/topic/', '/widget/'
#                             ])):
                            
#                             if href.startswith('/'):
#                                 base_url = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
#                                 href = base_url + href
                            
#                             if href.startswith('http'):
#                                 raw_articles.append({
#                                     'title': title,
#                                     'link': href
#                                 })
                    
#                     # Remove duplicates
#                     seen_links = set()
#                     unique_articles = []
#                     for article in raw_articles:
#                         if article['link'] not in seen_links:
#                             unique_articles.append(article)
#                             seen_links.add(article['link'])
                    
#                     print(f"📋 Found {len(unique_articles)} unique articles")
                    
#                     if len(unique_articles) > 0:
#                         articles_with_content = []
                        
#                         for article in unique_articles[:site['target']]:
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
#                                     content_hash = get_content_hash(article['title'], article_result.markdown)
                                    
#                                     if content_hash not in processed_hashes:
#                                         articles_with_content.append({
#                                             'title': article['title'],
#                                             'link': article['link'],
#                                             'content': article_result.markdown[:2500],
#                                             'hash': content_hash
#                                         })
#                                         processed_hashes.add(content_hash)
#                                         print(f"   ✓ {article['title'][:60]}...")
                                    
#                             except Exception as e:
#                                 continue
                        
#                         print(f"✅ Fetched {len(articles_with_content)} articles")
                        
#                         if articles_with_content:
#                             filtered_news = await smart_analyze_with_category(
#                                 articles_with_content, 
#                                 site['name']
#                             )
#                             all_news.extend(filtered_news)
                
#                 else:
#                     print(f"❌ Failed to fetch {site['name']}")
                    
#             except Exception as e:
#                 print(f"❌ Error scraping {site['name']}: {e}")
            
#             await asyncio.sleep(2)
    
#     return all_news


# async def smart_analyze_with_category(articles: List[Dict], source_name: str):
#     """AI analysis with proper categorization"""
#     global total_tokens_used, total_cost
    
#     print(f"\n🧠 Analyzing {source_name} articles...")
    
#     all_filtered = []
    
#     for i in range(0, len(articles), 3):
#         batch = articles[i:i+3]
        
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
# तुम्ही एक तज्ञ मराठी बातम्या विश्लेषक आहात. खालील बातम्यांचे विश्लेषण करा आणि प्रत्येक बातमीला योग्य category द्या.

# **Categories (फक्त यापैकी एक निवडा):**
# 1. sports - क्रीडा बातम्या
# 2. general - सामान्य महत्त्वाच्या बातम्या
# 3. crime - गुन्हेगारी बातम्या
# 4. politics - राजकीय बातम्या
# 5. education - शैक्षणिक बातम्या
# 6. economy - आर्थिक/व्यवसाय बातम्या
# 7. entertainment - मनोरंजन बातम्या
# 8. horror - भयानक/दुःखद घटना

# **JSON format:**
# [
#   {{
#     "title": "मूळ शीर्षक",
#     "category": "category name",
#     "detailed_summary": "विस्तृत सारांश 150-250 शब्दांत",
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
#                 max_tokens=3000
#             )
            
#             if hasattr(response, 'usage'):
#                 batch_tokens = response.usage.total_tokens
#                 total_tokens_used += batch_tokens
#                 batch_cost = (batch_tokens / 1_000_000) * 1.0
#                 total_cost += batch_cost
            
#             content = response.choices[0].message.content
#             json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
#             if json_match:
#                 batch_articles = json.loads(json_match.group())
#                 all_filtered.extend(batch_articles)
#                 print(f"   ✅ Extracted {len(batch_articles)} articles")
            
#         except Exception as e:
#             print(f"   ❌ AI analysis error: {e}")
        
#         await asyncio.sleep(1)
    
#     for article in all_filtered:
#         article['source'] = source_name
#         article['scraped_at'] = datetime.now().isoformat()
    
#     return all_filtered


# async def create_reel_script_single(news_article: Dict):
#     """Generate Instagram Reel script for a SINGLE news article"""
#     global total_tokens_used, total_cost
    
#     category = news_article.get('category', 'general')
    
#     system_prompt = """
# तुम्ही "जबरी खबरी" Instagram Reels चे एक्सपर्ट स्क्रिप्ट रायटर आहात.

# **HOOK VARIETY (पहिल्या 2 ओळी):**
# 1. Shock Statement: "एका अपघाताने संपूर्ण राज्य हादरलं."
# 2. Direct Question: "तुम्हाला माहिती आहे का...?"
# 3. Breaking News: "नुकतीच एक धक्कादायक माहिती समोर आली."
# 4. Name Drop: "[व्यक्ती नाव] आज चर्चेत का आहे?"
# 5. Contrast/Twist: "दिसतं काहीतरी, पण वास्तव वेगळंच."

# **स्ट्रक्चर (15-18 ओळी):**
# - पहिले 2 ओळी: Hook
# - 3-10 ओळी: मुख्य घटना
# - 11-14 ओळी: ट्विस्ट/प्रश्न
# - शेवटच्या 2-3 ओळी: CTA

# **ENDING:**
# "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

# OUTPUT: फक्त स्क्रिप्ट, 15-18 ओळी
# """
    
#     user_prompt = f"""
# खालील बातमीवर Instagram Reel script तयार करा.

# **बातमी:**
# शीर्षक: {news_article['title']}
# Category: {category}
# सारांश: {news_article['detailed_summary']}
# मुद्दे: {', '.join(news_article.get('key_points', []))}

# फक्त स्क्रिप्ट द्या, 15-18 ओळी.
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
        
#         if hasattr(response, 'usage'):
#             script_tokens = response.usage.total_tokens
#             total_tokens_used += script_tokens
#             total_cost += (script_tokens / 1_000_000) * 1.0
        
#         script = response.choices[0].message.content.strip()
#         script = script.replace('```', '').strip()
        
#         return script
        
#     except Exception as e:
#         print(f"❌ Error generating script: {e}")
#         return None


# async def main():
#     global total_tokens_used, total_cost
    
#     print("="*80)
#     print("🚀 SMART MARATHI NEWS SCRAPER + SCRIPT GENERATOR v2.0")
#     print("="*80)
#     print("📍 Target: 50+ different news articles")
#     print("📋 Categories: Sports, General, Crime, Politics, Education, Economy, Entertainment, Horror")
#     print("🎬 Output: Individual scripts for each news")
#     print("💾 Storage: Google Sheets with category column")
#     print("="*80 + "\n")
    
#     start_time = datetime.now()
    
#     # STEP 1: SCRAPING
#     print("\n" + "="*80)
#     print("STEP 1: SCRAPING NEWS FROM MULTIPLE SOURCES")
#     print("="*80 + "\n")
    
#     all_articles = await scrape_multiple_marathi_sources()
    
#     # Remove duplicates
#     unique_articles = []
#     seen_hashes = set()
    
#     for article in all_articles:
#         article_hash = article.get('hash', get_content_hash(article['title'], article.get('detailed_summary', '')))
#         if article_hash not in seen_hashes:
#             unique_articles.append(article)
#             seen_hashes.add(article_hash)
    
#     print(f"\n✅ Total unique articles: {len(unique_articles)}")
    
#     # Category breakdown
#     category_counts = {}
#     for article in unique_articles:
#         cat = article.get('category', 'general')
#         category_counts[cat] = category_counts.get(cat, 0) + 1
    
#     print("\n📊 Category Breakdown:")
#     for cat, count in sorted(category_counts.items()):
#         print(f"   {cat.upper()}: {count}")
    
#     # Select top 50 articles
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     unique_articles.sort(key=lambda x: priority_order.get(x.get('importance', 'medium'), 2))
    
#     selected_articles = unique_articles[:50]
    
#     print(f"\n🎯 Selected {len(selected_articles)} articles for scripts")
    
#     end_scrape = datetime.now()
#     scrape_duration = (end_scrape - start_time).total_seconds()
#     print(f"⏱️  Scraping: {scrape_duration:.2f} seconds\n")
    
#     # STEP 2: SCRIPT GENERATION
#     print("="*80)
#     print("STEP 2: GENERATING SCRIPTS & SAVING TO GOOGLE SHEETS")
#     print("="*80 + "\n")
    
#     worksheet = setup_google_sheets()
    
#     if worksheet and len(selected_articles) > 0:
#         successful_saves = 0
#         failed_saves = 0
        
#         for idx, article in enumerate(selected_articles, 1):
#             print(f"\n[{idx}/{len(selected_articles)}] {article['title'][:60]}...")
            
#             script = await create_reel_script_single(article)
            
#             if script:
#                 success = save_to_google_sheets(
#                     worksheet,
#                     article.get('category', 'general'),
#                     article['title'],
#                     script,
#                     article['link']
#                 )
                
#                 if success:
#                     successful_saves += 1
#                 else:
#                     failed_saves += 1
#             else:
#                 failed_saves += 1
            
#             await asyncio.sleep(1.5)
        
#         print("\n" + "="*80)
#         print("✅ COMPLETE!")
#         print("="*80)
#         print(f"   Successfully saved: {successful_saves}")
#         print(f"   Failed: {failed_saves}")
#         print(f"   📊 View: https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")
#     else:
#         print("⚠️ No articles or Google Sheets unavailable")
    
#     end_time = datetime.now()
#     total_duration = (end_time - start_time).total_seconds()
    
#     print("\n" + "="*80)
#     print("📈 SUMMARY")
#     print("="*80)
#     print(f"   Articles scraped: {len(unique_articles)}")
#     print(f"   Scripts generated: {successful_saves}")
#     print(f"   Time: {total_duration:.2f} seconds")
#     print(f"   Tokens: {total_tokens_used:,}")
#     print(f"   Cost: ${total_cost:.4f}")
#     print("="*80 + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())






# import asyncio
# import json
# from datetime import datetime, date
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
# from bs4 import BeautifulSoup
# from openai import OpenAI
# import re
# import gspread
# from google.oauth2.service_account import Credentials
# import os
# from typing import List, Dict
# import hashlib


# # ============================================================
# # Initialize Perplexity client - sonar-reasoning-pro
# # ============================================================
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),
#     base_url="https://api.perplexity.ai"
# )

# MODEL_NAME = "sonar-reasoning-pro"  # Updated model
# COST_PER_INPUT_TOKEN = 2.0 / 1_000_000   # $2 per 1M input tokens
# COST_PER_OUTPUT_TOKEN = 8.0 / 1_000_000  # $8 per 1M output tokens


# # ============================================================
# # Google Sheets Configuration
# # ============================================================
# GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
# GOOGLE_SHEET_NAME = "Instagram Scripts"
# GOOGLE_WORKSHEET_NAME = "Scripts"


# # ============================================================
# # Categories
# # ============================================================
# VALID_CATEGORIES = [
#     "sports", "general", "crime", "politics",
#     "education", "economy", "entertainment", "horror"
# ]


# # ============================================================
# # Token tracking
# # ============================================================
# total_input_tokens = 0
# total_output_tokens = 0
# total_cost = 0.0
# processed_hashes = set()


# # ============================================================
# # 5 News Sites - 10 articles each = 50 total
# # ============================================================
# NEWS_SITES = [
#     {
#         "name": "TV9 Marathi",
#         "url": "https://www.tv9marathi.com/latest-news",
#         "link_pattern": "tv9marathi.com",
#         "target": 10
#     },
#     {
#         "name": "ABP Majha",
#         "url": "https://marathi.abplive.com/news",
#         "link_pattern": "abplive.com",
#         "target": 10
#     },
#     {
#         "name": "Lokmat",
#         "url": "https://www.lokmat.com/latestnews/",
#         "link_pattern": "lokmat.com",
#         "target": 10
#     },
#     {
#         "name": "Maharashtra Times",
#         "url": "https://maharashtratimes.com/",
#         "link_pattern": "maharashtratimes.com",
#         "target": 10
#     },
#     {
#         "name": "NDTV Marathi",
#         "url": "https://marathi.ndtv.com/",
#         "link_pattern": "marathi.ndtv.com",
#         "target": 10
#     }
# ]


# # ============================================================
# # Google Sheets Setup
# # ============================================================
# def setup_google_sheets():
#     """Initialize Google Sheets connection"""
#     try:
#         scope = [
#             'https://spreadsheets.google.com/feeds',
#             'https://www.googleapis.com/auth/drive'
#         ]

#         creds = Credentials.from_service_account_file(
#             GOOGLE_SHEETS_CREDENTIALS_FILE,
#             scopes=scope
#         )

#         client = gspread.authorize(creds)

#         try:
#             sheet = client.open(GOOGLE_SHEET_NAME)
#             print(f"✅ Connected to existing sheet: '{GOOGLE_SHEET_NAME}'")
#         except gspread.SpreadsheetNotFound:
#             sheet = client.create(GOOGLE_SHEET_NAME)
#             print(f"✅ Created new sheet: '{GOOGLE_SHEET_NAME}'")

#         try:
#             worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
#             print(f"✅ Using worksheet: '{GOOGLE_WORKSHEET_NAME}'")
#         except gspread.WorksheetNotFound:
#             worksheet = sheet.add_worksheet(
#                 title=GOOGLE_WORKSHEET_NAME,
#                 rows=5000,
#                 cols=10
#             )
#             worksheet.update('A1:E1', [[
#                 'Timestamp', 'Category', 'Title', 'Script', 'Source Link'
#             ]])
#             worksheet.format('A1:E1', {
#                 'textFormat': {
#                     'bold': True,
#                     'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
#                 },
#                 'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
#                 'horizontalAlignment': 'CENTER'
#             })
#             worksheet.set_column_width('A', 180)
#             worksheet.set_column_width('B', 150)
#             worksheet.set_column_width('C', 400)
#             worksheet.set_column_width('D', 600)
#             worksheet.set_column_width('E', 400)
#             print(f"✅ Created new worksheet with headers")

#         return worksheet

#     except FileNotFoundError:
#         print(f"❌ Error: '{GOOGLE_SHEETS_CREDENTIALS_FILE}' not found!")
#         return None
#     except Exception as e:
#         print(f"❌ Google Sheets setup error: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# # ============================================================
# # Save to Google Sheets
# # ============================================================
# def save_to_google_sheets(worksheet, category, title, script, source_link):
#     """Save script to Google Sheets"""
#     try:
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         if isinstance(script, list):
#             script = '\n'.join(str(item) for item in script)
#         else:
#             script = str(script).strip()

#         script = script.replace('[', '').replace(']', '')
#         title = str(title).strip()
#         source_link = str(source_link).strip()
#         category = str(category).strip().lower()

#         if category not in VALID_CATEGORIES:
#             category = "general"

#         row_data = [timestamp, category, title, script, source_link]

#         next_row = len(worksheet.get_all_values()) + 1
#         worksheet.append_row(row_data, value_input_option='RAW')

#         worksheet.format(f'A{next_row}:E{next_row}', {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })

#         category_colors = {
#             'crime':         {'red': 0.95, 'green': 0.8,  'blue': 0.8},
#             'politics':      {'red': 0.8,  'green': 0.9,  'blue': 1.0},
#             'sports':        {'red': 0.8,  'green': 1.0,  'blue': 0.8},
#             'entertainment': {'red': 1.0,  'green': 0.9,  'blue': 0.8},
#             'education':     {'red': 0.9,  'green': 0.95, 'blue': 1.0},
#             'economy':       {'red': 0.95, 'green': 1.0,  'blue': 0.85},
#             'horror':        {'red': 0.7,  'green': 0.7,  'blue': 0.7},
#             'general':       {'red': 1.0,  'green': 1.0,  'blue': 0.9}
#         }

#         worksheet.format(f'B{next_row}', {
#             'textFormat': {
#                 'bold': True,
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': category_colors.get(category, category_colors['general']),
#             'horizontalAlignment': 'CENTER'
#         })

#         print(f"✅ Saved [{category.upper()}] {title[:50]}...")
#         return True

#     except Exception as e:
#         print(f"❌ Error saving to Google Sheets: {e}")
#         return False


# # ============================================================
# # Content Hash for Duplicate Detection
# # ============================================================
# def get_content_hash(title: str, content: str) -> str:
#     combined = f"{title.lower()}{content[:200].lower()}"
#     return hashlib.md5(combined.encode()).hexdigest()


# # ============================================================
# # Web Scraping - 5 Sites × 10 Articles = 50
# # ============================================================
# async def scrape_multiple_marathi_sources():
#     """Scrape exactly 10 articles from each of 5 sites = 50 total"""

#     all_news = []

#     async with AsyncWebCrawler(verbose=False) as crawler:

#         for site in NEWS_SITES:
#             print(f"\n{'='*60}")
#             print(f"🔍 Scraping {site['name']} (Target: {site['target']} articles)")
#             print(f"{'='*60}")

#             try:
#                 config = CrawlerRunConfig(
#                     cache_mode=CacheMode.BYPASS,
#                     wait_for="body",
#                     word_count_threshold=10,
#                     page_timeout=30000,
#                     js_code="await new Promise(r => setTimeout(r, 2000));"
#                 )

#                 result = await crawler.arun(site['url'], config=config)

#                 if result.success:
#                     soup = BeautifulSoup(result.html, 'html.parser')
#                     raw_articles = []
#                     all_links = soup.find_all('a', href=True)

#                     for link_tag in all_links:
#                         href = link_tag.get('href', '')
#                         title = link_tag.get_text(strip=True)

#                         if (len(title) > 15 and len(title) < 300 and
#                             site['link_pattern'] in href and
#                             not any(x in href.lower() for x in [
#                                 'javascript:', 'mailto:', '#',
#                                 '/category/', '/tag/', '/author/',
#                                 'facebook.com', 'twitter.com', 'instagram.com',
#                                 'youtube.com', 'whatsapp.com', '/myaccount/',
#                                 '/install_app', '/advertisement', '/epaper',
#                                 'web-stories', 'photo-gallery', '/videos/',
#                                 '/games/', '/jokes/', '/terms-and-conditions',
#                                 '/topic/', '/widget/'
#                             ])):

#                             if href.startswith('/'):
#                                 base_url = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
#                                 href = base_url + href

#                             if href.startswith('http'):
#                                 raw_articles.append({
#                                     'title': title,
#                                     'link': href
#                                 })

#                     # Remove duplicates
#                     seen_links = set()
#                     unique_articles = []
#                     for article in raw_articles:
#                         if article['link'] not in seen_links:
#                             unique_articles.append(article)
#                             seen_links.add(article['link'])

#                     print(f"📋 Found {len(unique_articles)} unique links")

#                     # Fetch content for exactly 'target' articles
#                     articles_with_content = []
#                     fetch_attempts = 0

#                     for article in unique_articles:
#                         if len(articles_with_content) >= site['target']:
#                             break

#                         fetch_attempts += 1

#                         try:
#                             article_result = await crawler.arun(
#                                 article['link'],
#                                 config=CrawlerRunConfig(
#                                     cache_mode=CacheMode.BYPASS,
#                                     word_count_threshold=50,
#                                     page_timeout=15000
#                                 )
#                             )

#                             if article_result.success and len(article_result.markdown) > 100:
#                                 content_hash = get_content_hash(
#                                     article['title'],
#                                     article_result.markdown
#                                 )

#                                 if content_hash not in processed_hashes:
#                                     articles_with_content.append({
#                                         'title': article['title'],
#                                         'link': article['link'],
#                                         'content': article_result.markdown[:2500],
#                                         'hash': content_hash
#                                     })
#                                     processed_hashes.add(content_hash)
#                                     print(f"   ✓ [{len(articles_with_content)}/{site['target']}] {article['title'][:55]}...")

#                         except Exception:
#                             continue

#                     print(f"✅ {site['name']}: Fetched {len(articles_with_content)} articles")

#                     # AI Analysis for this site's articles
#                     if articles_with_content:
#                         filtered_news = await smart_analyze_with_category(
#                             articles_with_content,
#                             site['name']
#                         )
#                         all_news.extend(filtered_news)
#                         print(f"🧠 {site['name']}: Analyzed {len(filtered_news)} articles")

#                 else:
#                     print(f"❌ Failed to fetch {site['name']}")

#             except Exception as e:
#                 print(f"❌ Error scraping {site['name']}: {e}")

#             # Delay between sites
#             print(f"⏳ Waiting before next site...")
#             await asyncio.sleep(3)

#     return all_news


# # ============================================================
# # AI Categorization using sonar-reasoning-pro
# # ============================================================
# async def smart_analyze_with_category(articles: List[Dict], source_name: str):
#     """AI categorization with sonar-reasoning-pro in batches of 5"""
#     global total_input_tokens, total_output_tokens, total_cost

#     all_filtered = []

#     # Process in batches of 5 for efficiency
#     for i in range(0, len(articles), 5):
#         batch = articles[i:i+5]

#         articles_text = ""
#         for idx, article in enumerate(batch, i+1):
#             articles_text += f"""
# बातमी #{idx}:
# शीर्षक: {article['title']}
# Link: {article['link']}
# Content: {article['content'][:1000]}
# ---
# """

#         prompt = f"""
# तुम्ही एक तज्ञ मराठी बातम्या विश्लेषक आहात. खालील बातम्यांचे विश्लेषण करा.

# **Categories (फक्त यापैकी एक निवडा):**
# 1. sports - क्रीडा बातम्या
# 2. general - सामान्य महत्त्वाच्या बातम्या
# 3. crime - गुन्हेगारी बातम्या
# 4. politics - राजकीय बातम्या
# 5. education - शैक्षणिक बातम्या
# 6. economy - आर्थिक बातम्या
# 7. entertainment - मनोरंजन बातम्या
# 8. horror - भयानक घटना

# **JSON format (फक्त valid JSON array return करा):**
# [
#   {{
#     "title": "मूळ शीर्षक",
#     "category": "category name",
#     "detailed_summary": "विस्तृत सारांश 150-200 शब्दांत - कोण, काय, कुठे, कधी, कसे सर्व details सह",
#     "importance": "high/medium/low",
#     "link": "URL जसाच्या तसा",
#     "key_points": ["मुद्दा 1", "मुद्दा 2", "मुद्दा 3"]
#   }}
# ]

# **बातम्या:**
# {articles_text}

# फक्त JSON array return करा. कोणतेही explanation नाही.
# """

#         try:
#             response = perplexity_client.chat.completions.create(
#                 model=MODEL_NAME,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are an expert Marathi news analyst. Return ONLY valid JSON array. No markdown, no explanation."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.2,
#                 max_tokens=4000
#             )

#             # Track tokens
#             if hasattr(response, 'usage'):
#                 input_t = response.usage.prompt_tokens
#                 output_t = response.usage.completion_tokens
#                 total_input_tokens += input_t
#                 total_output_tokens += output_t
#                 batch_cost = (input_t * COST_PER_INPUT_TOKEN) + (output_t * COST_PER_OUTPUT_TOKEN)
#                 total_cost += batch_cost
#                 print(f"   📊 Batch tokens: {input_t}in + {output_t}out = ${batch_cost:.4f}")

#             content = response.choices[0].message.content

#             # Clean thinking tags if present (sonar-reasoning-pro returns <think> tags)
#             content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

#             json_match = re.search(r'\[.*\]', content, re.DOTALL)

#             if json_match:
#                 batch_articles = json.loads(json_match.group())
#                 all_filtered.extend(batch_articles)
#                 print(f"   ✅ Categorized {len(batch_articles)} articles")
#             else:
#                 print(f"   ⚠️ Could not parse JSON from response")

#         except json.JSONDecodeError as e:
#             print(f"   ❌ JSON parse error: {e}")
#         except Exception as e:
#             print(f"   ❌ AI analysis error: {e}")

#         await asyncio.sleep(1.5)

#     # Add source metadata
#     for article in all_filtered:
#         article['source'] = source_name
#         article['scraped_at'] = datetime.now().isoformat()

#     return all_filtered


# # ============================================================
# # Script Generation using sonar-reasoning-pro
# # ============================================================
# async def create_reel_script_single(news_article: Dict):
#     """Generate Instagram Reel script using sonar-reasoning-pro"""
#     global total_input_tokens, total_output_tokens, total_cost

#     category = news_article.get('category', 'general')

#     system_prompt = """तुम्ही "जबरी खबरी" Instagram Reels चे एक्सपर्ट स्क्रिप्ट रायटर आहात.

# **HOOK VARIETY (पहिल्या 2 ओळी - दर वेळी वेगळी style):**
# 1. Shock Statement: "एका अपघाताने संपूर्ण राज्य हादरलं."
# 2. Direct Question: "तुम्हाला माहिती आहे का...?"
# 3. Breaking News: "नुकतीच एक धक्कादायक माहिती समोर आली."
# 4. Name Drop: "[व्यक्ती नाव] आज चर्चेत का आहे?"
# 5. Contrast/Twist: "दिसतं काहीतरी, पण वास्तव वेगळंच."
# 6. Suspense: "काल रात्री घडलं ते तुम्हाला विश्वास बसणार नाही..."
# 7. Urgency: "महाराष्ट्रात मोठी घडामोड..."

# **स्ट्रक्चर (15-18 ओळी):**
# - ओळ 1-2: Hook (लक्ष वेधणारी सुरुवात)
# - ओळ 3-10: मुख्य घटना (सर्व facts, नावे, ठिकाणे, संख्या सह)
# - ओळ 11-14: ट्विस्ट/विश्लेषण/प्रश्न
# - ओळ 15-18: Call To Action

# **नियम:**
# - Conversational Marathi भाषा
# - प्रत्येक ओळ छोटी (1-2 वाक्य)
# - Suspense आणि curiosity राखा
# - Real facts वापरा

# **शेवट नक्की असा:**
# "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

# OUTPUT: फक्त script, 15-18 ओळी, इतर काहीही नाही."""

#     user_prompt = f"""खालील {category.upper()} बातमीवर Instagram Reel script तयार करा.

# शीर्षक: {news_article['title']}
# सारांश: {news_article.get('detailed_summary', '')}
# Key Points: {', '.join(news_article.get('key_points', []))}
# Source: {news_article.get('source', '')}

# 15-18 ओळींची script द्या. फक्त script, बाकी काही नाही."""

#     try:
#         response = perplexity_client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.8,
#             max_tokens=1500
#         )

#         # Track tokens
#         if hasattr(response, 'usage'):
#             input_t = response.usage.prompt_tokens
#             output_t = response.usage.completion_tokens
#             total_input_tokens += input_t
#             total_output_tokens += output_t
#             script_cost = (input_t * COST_PER_INPUT_TOKEN) + (output_t * COST_PER_OUTPUT_TOKEN)
#             total_cost += script_cost

#         script = response.choices[0].message.content.strip()

#         # Remove thinking tags from sonar-reasoning-pro
#         script = re.sub(r'<think>.*?</think>', '', script, flags=re.DOTALL).strip()
#         script = script.replace('```', '').strip()

#         return script

#     except Exception as e:
#         print(f"❌ Script generation error: {e}")
#         return None


# # ============================================================
# # Main Pipeline
# # ============================================================
# async def main():
#     global total_input_tokens, total_output_tokens, total_cost

#     print("=" * 70)
#     print("🚀 JABARI KHABRI - SMART NEWS SCRAPER v3.0")
#     print(f"🤖 Model: {MODEL_NAME}")
#     print("=" * 70)
#     print("📍 Sites  : TV9 Marathi, ABP Majha, Lokmat, Mah Times, NDTV Marathi")
#     print("📊 Target : 10 articles × 5 sites = 50 total scripts")
#     print("🎬 Output : 50 Reel Scripts → Google Sheets")
#     print("=" * 70 + "\n")

#     start_time = datetime.now()

#     # ─── STEP 1: SCRAPING ────────────────────────────────────────────
#     print("\n" + "=" * 70)
#     print("STEP 1: SCRAPING 5 MARATHI NEWS SITES")
#     print("=" * 70 + "\n")

#     all_articles = await scrape_multiple_marathi_sources()

#     # Final deduplication
#     unique_articles = []
#     seen_hashes = set()

#     for article in all_articles:
#         article_hash = article.get(
#             'hash',
#             get_content_hash(article['title'], article.get('detailed_summary', ''))
#         )
#         if article_hash not in seen_hashes:
#             unique_articles.append(article)
#             seen_hashes.add(article_hash)

#     print(f"\n✅ Total unique articles after dedup: {len(unique_articles)}")

#     # Category breakdown
#     category_counts = {}
#     for article in unique_articles:
#         cat = article.get('category', 'general')
#         category_counts[cat] = category_counts.get(cat, 0) + 1

#     print("\n📊 Category Breakdown:")
#     for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
#         bar = "█" * count
#         print(f"   {cat.upper():<15} {bar} ({count})")


#     # Sort by importance and take top 50
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     unique_articles.sort(
#         key=lambda x: priority_order.get(x.get('importance', 'medium'), 2)
#     )
#     selected_articles = unique_articles[:50]

#     print(f"\n🎯 Selected top {len(selected_articles)} articles for script generation")

#     scrape_duration = (datetime.now() - start_time).total_seconds()
#     print(f"⏱️  Scraping done in {scrape_duration:.0f} seconds\n")

#     # ─── STEP 2: SCRIPT GENERATION + SHEETS ──────────────────────────
#     print("=" * 70)
#     print("STEP 2: GENERATING 50 REEL SCRIPTS → GOOGLE SHEETS")
#     print("=" * 70 + "\n")

#     worksheet = setup_google_sheets()

#     successful_saves = 0
#     failed_saves = 0

#     if worksheet and selected_articles:
#         for idx, article in enumerate(selected_articles, 1):
#             print(f"\n[{idx:02d}/50] {article.get('source', '')} | "
#                   f"{article.get('category', '').upper()} | "
#                   f"{article['title'][:50]}...")

#             script = await create_reel_script_single(article)

#             if script:
#                 success = save_to_google_sheets(
#                     worksheet,
#                     article.get('category', 'general'),
#                     article['title'],
#                     script,
#                     article.get('link', '')
#                 )
#                 if success:
#                     successful_saves += 1
#                 else:
#                     failed_saves += 1
#             else:
#                 failed_saves += 1
#                 print(f"   ❌ Script generation failed")

#             # Delay to respect rate limits
#             await asyncio.sleep(2)

#         print("\n" + "=" * 70)
#         print("✅ ALL SCRIPTS GENERATED!")
#         print("=" * 70)
#         print(f"   ✅ Successfully saved : {successful_saves}/50")
#         print(f"   ❌ Failed             : {failed_saves}")
#         print(f"   📊 Google Sheet       : https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")

#     else:
#         print("⚠️ No articles found or Google Sheets unavailable!")

#     # ─── FINAL SUMMARY ───────────────────────────────────────────────
#     total_duration = (datetime.now() - start_time).total_seconds()
#     total_tokens = total_input_tokens + total_output_tokens

#     print("\n" + "=" * 70)
#     print("📈 FINAL SUMMARY")
#     print("=" * 70)
#     print(f"   🤖 Model              : {MODEL_NAME}")
#     print(f"   📰 Articles scraped   : {len(unique_articles)}")
#     print(f"   ✅ Scripts generated  : {successful_saves}")
#     print(f"   ⏱️  Total time         : {total_duration:.0f} seconds ({total_duration/60:.1f} mins)")
#     print(f"   📥 Input tokens       : {total_input_tokens:,}")
#     print(f"   📤 Output tokens      : {total_output_tokens:,}")
#     print(f"   🔢 Total tokens       : {total_tokens:,}")
#     print(f"   💰 Total cost         : ${total_cost:.4f} (~₹{total_cost*84:.2f})")
#     print(f"   💵 Cost per script    : ${total_cost/max(successful_saves,1):.4f}")
#     print("=" * 70 + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())







# ---------------------working 50 scripts --------------

# import asyncio
# import json
# from datetime import datetime, date
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
# from bs4 import BeautifulSoup
# from openai import OpenAI
# import re
# import gspread
# from google.oauth2.service_account import Credentials
# import os
# from typing import List, Dict
# import hashlib


# # ============================================================
# # Perplexity Client
# # ============================================================
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),
#     base_url="https://api.perplexity.ai"
# )

# ANALYSIS_MODEL      = "sonar-pro"           # ✅ Cheaper for categorization
# SCRIPT_MODEL        = "sonar-reasoning-pro" # ✅ Quality for scripts

# ANALYSIS_INPUT_COST  = 1.0 / 1_000_000
# ANALYSIS_OUTPUT_COST = 1.0 / 1_000_000
# SCRIPT_INPUT_COST    = 2.0 / 1_000_000
# SCRIPT_OUTPUT_COST   = 8.0 / 1_000_000


# # ============================================================
# # Config
# # ============================================================
# GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
# GOOGLE_SHEET_NAME               = "Instagram Scripts"
# GOOGLE_WORKSHEET_NAME           = "Scripts"
# TARGET_SCRIPTS                  = 50   # ✅ Hard target

# VALID_CATEGORIES = [
#     "sports", "general", "crime", "politics",
#     "education", "economy", "entertainment", "horror"
# ]


# # ============================================================
# # Token tracking
# # ============================================================
# total_input_tokens  = 0
# total_output_tokens = 0
# total_cost          = 0.0
# processed_hashes    = set()


# # ============================================================
# # 5 News Sites
# # ============================================================
# NEWS_SITES = [
#     {
#         "name": "TV9 Marathi",
#         "url": "https://www.tv9marathi.com/latest-news",
#         "link_pattern": "tv9marathi.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "ABP Majha",
#         "url": "https://marathi.abplive.com/news",
#         "link_pattern": "abplive.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "Lokmat",
#         "url": "https://www.lokmat.com/latestnews/",
#         "link_pattern": "lokmat.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "Maharashtra Times",
#         "url": "https://maharashtratimes.com/",
#         "link_pattern": "maharashtratimes.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "NDTV Marathi",
#         "url": "https://marathi.ndtv.com/",
#         "link_pattern": "marathi.ndtv.com",
#         "target": 10,
#         "fetch_limit": 40
#     }
# ]


# # ============================================================
# # Google Sheets Setup
# # ============================================================
# def setup_google_sheets():
#     try:
#         scope = [
#             'https://spreadsheets.google.com/feeds',
#             'https://www.googleapis.com/auth/drive'
#         ]
#         creds = Credentials.from_service_account_file(
#             GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scope
#         )
#         client = gspread.authorize(creds)

#         try:
#             sheet = client.open(GOOGLE_SHEET_NAME)
#             print(f"✅ Connected: '{GOOGLE_SHEET_NAME}'")
#         except gspread.SpreadsheetNotFound:
#             sheet = client.create(GOOGLE_SHEET_NAME)
#             print(f"✅ Created: '{GOOGLE_SHEET_NAME}'")

#         try:
#             worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
#             print(f"✅ Worksheet: '{GOOGLE_WORKSHEET_NAME}'")
#         except gspread.WorksheetNotFound:
#             worksheet = sheet.add_worksheet(
#                 title=GOOGLE_WORKSHEET_NAME, rows=5000, cols=10
#             )
#             worksheet.update('A1:E1', [[
#                 'Timestamp', 'Category', 'Title', 'Script', 'Source Link'
#             ]])
#             worksheet.format('A1:E1', {
#                 'textFormat': {
#                     'bold': True,
#                     'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
#                 },
#                 'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
#                 'horizontalAlignment': 'CENTER'
#             })
#             worksheet.set_column_width('A', 180)
#             worksheet.set_column_width('B', 150)
#             worksheet.set_column_width('C', 400)
#             worksheet.set_column_width('D', 600)
#             worksheet.set_column_width('E', 400)
#             print(f"✅ Created worksheet with headers")

#         return worksheet

#     except FileNotFoundError:
#         print(f"❌ credentials.json not found!")
#         return None
#     except Exception as e:
#         print(f"❌ Sheets setup error: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# # ============================================================
# # Save to Google Sheets
# # ============================================================
# def save_to_google_sheets(worksheet, category, title, script, source_link):
#     try:
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         script = '\n'.join(str(i) for i in script) if isinstance(script, list) else str(script).strip()
#         script = script.replace('[', '').replace(']', '')
#         title = str(title).strip()
#         source_link = str(source_link).strip()
#         category = str(category).strip().lower()

#         if category not in VALID_CATEGORIES:
#             category = "general"

#         next_row = len(worksheet.get_all_values()) + 1
#         worksheet.append_row(
#             [timestamp, category, title, script, source_link],
#             value_input_option='RAW'
#         )

#         worksheet.format(f'A{next_row}:E{next_row}', {
#             'textFormat': {'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}, 'fontSize': 10},
#             'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })

#         category_colors = {
#             'crime':         {'red': 0.95, 'green': 0.8,  'blue': 0.8},
#             'politics':      {'red': 0.8,  'green': 0.9,  'blue': 1.0},
#             'sports':        {'red': 0.8,  'green': 1.0,  'blue': 0.8},
#             'entertainment': {'red': 1.0,  'green': 0.9,  'blue': 0.8},
#             'education':     {'red': 0.9,  'green': 0.95, 'blue': 1.0},
#             'economy':       {'red': 0.95, 'green': 1.0,  'blue': 0.85},
#             'horror':        {'red': 0.7,  'green': 0.7,  'blue': 0.7},
#             'general':       {'red': 1.0,  'green': 1.0,  'blue': 0.9}
#         }
#         worksheet.format(f'B{next_row}', {
#             'textFormat': {'bold': True, 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}, 'fontSize': 10},
#             'backgroundColor': category_colors.get(category, category_colors['general']),
#             'horizontalAlignment': 'CENTER'
#         })

#         print(f"✅ Saved [{category.upper()}] {title[:50]}...")
#         return True

#     except Exception as e:
#         print(f"❌ Save error: {e}")
#         return False


# # ============================================================
# # Content Hash
# # ============================================================
# def get_content_hash(title: str, content: str) -> str:
#     return hashlib.md5(f"{title.lower()}{content[:200].lower()}".encode()).hexdigest()


# # ============================================================
# # Fetch with Retry
# # ============================================================
# async def fetch_article_with_retry(crawler, url: str, retries: int = 3) -> str:
#     for attempt in range(1, retries + 1):
#         try:
#             result = await crawler.arun(
#                 url,
#                 config=CrawlerRunConfig(
#                     cache_mode=CacheMode.BYPASS,
#                     word_count_threshold=10,
#                     page_timeout=25000
#                 )
#             )
#             if result.success and len(result.markdown) > 50:
#                 return result.markdown
#             await asyncio.sleep(2)
#         except Exception:
#             await asyncio.sleep(2)
#     return ""


# # ============================================================
# # Web Scraping
# # ============================================================
# async def scrape_multiple_marathi_sources():
#     all_news = []

#     async with AsyncWebCrawler(verbose=False) as crawler:
#         for site in NEWS_SITES:
#             print(f"\n{'='*60}")
#             print(f"🔍 {site['name']} | Target: {site['target']}")
#             print(f"{'='*60}")

#             site_articles = []

#             try:
#                 result = await crawler.arun(
#                     site['url'],
#                     config=CrawlerRunConfig(
#                         cache_mode=CacheMode.BYPASS,
#                         wait_for="body",
#                         word_count_threshold=10,
#                         page_timeout=30000,
#                         js_code="await new Promise(r => setTimeout(r, 3000));"
#                     )
#                 )

#                 if not result.success:
#                     print(f"❌ Failed: {site['name']}")
#                     continue

#                 soup = BeautifulSoup(result.html, 'html.parser')
#                 raw_articles = []

#                 for link_tag in soup.find_all('a', href=True):
#                     href  = link_tag.get('href', '')
#                     title = link_tag.get_text(strip=True)

#                     if (15 < len(title) < 300 and
#                         site['link_pattern'] in href and
#                         not any(x in href.lower() for x in [
#                             'javascript:', 'mailto:', '#',
#                             '/category/', '/tag/', '/author/',
#                             'facebook.com', 'twitter.com', 'instagram.com',
#                             'youtube.com', 'whatsapp.com', '/myaccount/',
#                             '/install_app', '/advertisement', '/epaper',
#                             'web-stories', 'photo-gallery', '/videos/',
#                             '/games/', '/jokes/', '/terms-and-conditions',
#                             '/topic/', '/widget/'
#                         ])):

#                         if href.startswith('/'):
#                             base = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
#                             href = base + href

#                         if href.startswith('http'):
#                             raw_articles.append({'title': title, 'link': href})

#                 # Deduplicate
#                 seen = set()
#                 unique_links = []
#                 for a in raw_articles:
#                     if a['link'] not in seen:
#                         unique_links.append(a)
#                         seen.add(a['link'])

#                 print(f"📋 Found {len(unique_links)} unique links")

#                 # Fetch articles until target reached
#                 for article in unique_links[:site['fetch_limit']]:
#                     if len(site_articles) >= site['target']:
#                         break

#                     print(f"   🔗 [{len(site_articles)+1}/{site['target']}] {article['title'][:50]}...")

#                     markdown = await fetch_article_with_retry(crawler, article['link'])

#                     # ✅ Always add article - use content if available, title as fallback
#                     content = markdown if markdown else article['title']
#                     content_hash = get_content_hash(article['title'], content)

#                     if content_hash not in processed_hashes:
#                         site_articles.append({
#                             'title':   article['title'],
#                             'link':    article['link'],
#                             'content': content[:2500],
#                             'hash':    content_hash,
#                             'has_full_content': bool(markdown)  # ✅ Track if real content
#                         })
#                         processed_hashes.add(content_hash)
#                         status = "✅" if markdown else "⚠️ fallback"
#                         print(f"   {status} [{len(site_articles)}/{site['target']}] {article['title'][:50]}...")
#                     else:
#                         print(f"   🔄 Duplicate skipped")

#                     await asyncio.sleep(1)

#                 print(f"\n📦 {site['name']}: {len(site_articles)}/{site['target']} collected")

#                 if site_articles:
#                     filtered = await smart_analyze_with_category(site_articles, site['name'])
#                     all_news.extend(filtered)
#                     print(f"🧠 {site['name']}: Analyzed {len(filtered)} articles")

#             except Exception as e:
#                 print(f"❌ Error {site['name']}: {e}")

#             await asyncio.sleep(3)

#     return all_news


# # ============================================================
# # AI Categorization - sonar-pro (cheap)
# # ============================================================
# async def smart_analyze_with_category(articles: List[Dict], source_name: str):
#     global total_input_tokens, total_output_tokens, total_cost

#     all_filtered = []

#     for i in range(0, len(articles), 5):
#         batch = articles[i:i+5]

#         articles_text = ""
#         for idx, article in enumerate(batch, i+1):
#             # ✅ Only 500 chars for analysis - enough to categorize
#             articles_text += f"#{idx}: {article['title']}\n{article['content'][:500]}\n---\n"

#         # ✅ Shorter prompt
#         prompt = f"""मराठी बातम्या विश्लेषक: खालील बातम्यांना category आणि summary द्या.

# Categories: sports, general, crime, politics, education, economy, entertainment, horror

# JSON array format:
# [{{"title":"शीर्षक","category":"cat","detailed_summary":"150 शब्द Marathi summary","importance":"high/medium/low","link":"url","key_points":["1","2","3"]}}]

# बातम्या:
# {articles_text}

# फक्त JSON array."""

#         try:
#             response = perplexity_client.chat.completions.create(
#                 model=ANALYSIS_MODEL,  # ✅ sonar-pro (cheaper)
#                 messages=[
#                     {"role": "system", "content": "Return ONLY valid JSON array."},
#                     {"role": "user",   "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=3000
#             )

#             if hasattr(response, 'usage'):
#                 i_t = response.usage.prompt_tokens
#                 o_t = response.usage.completion_tokens
#                 total_input_tokens  += i_t
#                 total_output_tokens += o_t
#                 c = (i_t * ANALYSIS_INPUT_COST) + (o_t * ANALYSIS_OUTPUT_COST)
#                 total_cost += c
#                 print(f"   📊 {i_t}in + {o_t}out = ${c:.4f}")

#             content = response.choices[0].message.content
#             content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
#             match = re.search(r'\[.*\]', content, re.DOTALL)

#             if match:
#                 parsed = json.loads(match.group())
#                 all_filtered.extend(parsed)
#                 print(f"   ✅ Categorized {len(parsed)} articles")
#             else:
#                 # ✅ FALLBACK: manually create entries if JSON fails
#                 print(f"   ⚠️ JSON failed - using fallback entries")
#                 for article in batch:
#                     all_filtered.append({
#                         'title':            article['title'],
#                         'category':         'general',
#                         'detailed_summary': article['title'],
#                         'importance':       'medium',
#                         'link':             article['link'],
#                         'key_points':       [article['title']]
#                     })

#         except json.JSONDecodeError:
#             # ✅ FALLBACK on JSON error too
#             for article in batch:
#                 all_filtered.append({
#                     'title':            article['title'],
#                     'category':         'general',
#                     'detailed_summary': article['content'][:300],
#                     'importance':       'medium',
#                     'link':             article['link'],
#                     'key_points':       [article['title']]
#                 })
#         except Exception as e:
#             print(f"   ❌ AI error: {e}")

#         await asyncio.sleep(1.5)

#     for article in all_filtered:
#         article['source']      = source_name
#         article['scraped_at']  = datetime.now().isoformat()

#     return all_filtered


# # ============================================================
# # Script Generation - sonar-reasoning-pro (quality)
# # ============================================================
# async def create_reel_script_single(news_article: Dict):
#     global total_input_tokens, total_output_tokens, total_cost

#     category = news_article.get('category', 'general')

#     # ✅ Shorter system prompt - same quality
#     system_prompt = """तुम्ही "जबरी खबरी" Reels script writer आहात.
# Hook (2 ओळी) → Story+Facts (8 ओळी) → Twist/Question (4 ओळी) → CTA (2-4 ओळी)
# शेवट: "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."
# Output: फक्त 15-18 ओळी script. इतर काहीही नाही."""

#     # ✅ Trim summary to 300 chars to save tokens
#     summary     = news_article.get('detailed_summary', news_article.get('title', ''))[:300]
#     key_points  = ', '.join(news_article.get('key_points', [news_article.get('title', '')]))

#     user_prompt = f"""{category.upper()} बातमी:
# शीर्षक: {news_article['title']}
# सारांश: {summary}
# मुद्दे: {key_points}

# 15-18 ओळी script द्या."""

#     # ✅ Retry script generation up to 2 times
#     for attempt in range(1, 3):
#         try:
#             response = perplexity_client.chat.completions.create(
#                 model=SCRIPT_MODEL,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user",   "content": user_prompt}
#                 ],
#                 temperature=0.8,
#                 max_tokens=1200  # ✅ Reduced from 1500
#             )

#             if hasattr(response, 'usage'):
#                 i_t = response.usage.prompt_tokens
#                 o_t = response.usage.completion_tokens
#                 total_input_tokens  += i_t
#                 total_output_tokens += o_t
#                 total_cost += (i_t * SCRIPT_INPUT_COST) + (o_t * SCRIPT_OUTPUT_COST)

#             script = response.choices[0].message.content.strip()
#             script = re.sub(r'<think>.*?</think>', '', script, flags=re.DOTALL).strip()
#             script = script.replace('```', '').strip()

#             if len(script) > 50:  # ✅ Valid script check
#                 return script

#         except Exception as e:
#             print(f"   ⚠️ Script attempt {attempt} failed: {e}")
#             await asyncio.sleep(2)

#     # ✅ LAST RESORT fallback script if all attempts fail
#     return f"""महाराष्ट्रात एक महत्त्वाची बातमी समोर आली आहे.

# {news_article['title']}

# ही बातमी सध्या चर्चेत आहे आणि सर्वांचे लक्ष वेधून घेत आहे.

# अधिक माहितीसाठी आमचे पेज फॉलो करा.

# तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."""


# # ============================================================
# # Main Pipeline
# # ============================================================
# async def main():
#     global total_input_tokens, total_output_tokens, total_cost

#     print("=" * 70)
#     print("🚀 JABARI KHABRI - SMART NEWS SCRAPER v4.0")
#     print(f"🔍 Analysis : {ANALYSIS_MODEL}")
#     print(f"✍️  Scripts  : {SCRIPT_MODEL}")
#     print("=" * 70)
#     print("📍 Sites  : TV9, ABP Majha, Lokmat, Mah Times, NDTV Marathi")
#     print(f"📊 Target : 10 × 5 = {TARGET_SCRIPTS} scripts STRICTLY")
#     print("🔁 Buffer : 40 links/site | 🔄 Retry: 3× fetch + 2× script")
#     print("=" * 70 + "\n")

#     start_time = datetime.now()

#     # ── STEP 1: SCRAPING ─────────────────────────────────────────────
#     print("=" * 70)
#     print("STEP 1: SCRAPING 5 MARATHI NEWS SITES")
#     print("=" * 70 + "\n")

#     all_articles = await scrape_multiple_marathi_sources()

#     # Final deduplication
#     unique_articles = []
#     seen_hashes = set()
#     for article in all_articles:
#         h = article.get('hash', get_content_hash(
#             article['title'], article.get('detailed_summary', '')
#         ))
#         if h not in seen_hashes:
#             unique_articles.append(article)
#             seen_hashes.add(h)

#     print(f"\n✅ Total unique articles: {len(unique_articles)}")

#     # ✅ FIXED category breakdown
#     category_counts = {}
#     for article in unique_articles:
#         cat = article.get('category', 'general')
#         category_counts[cat] = category_counts.get(cat, 0) + 1

#     print("\n📊 Category Breakdown:")
#     for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):  # ✅ FIXED[1]
#         bar = "█" * count
#         print(f"   {cat.upper():<15} {bar} ({count})")

#     # Sort by importance
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     unique_articles.sort(
#         key=lambda x: priority_order.get(x.get('importance', 'medium'), 2)
#     )
#     selected_articles = unique_articles[:TARGET_SCRIPTS]

#     print(f"\n🎯 Selected: {len(selected_articles)}/{TARGET_SCRIPTS} articles")
#     print(f"⏱️  Scraping: {(datetime.now()-start_time).total_seconds():.0f}s\n")

#     # ── STEP 2: SCRIPTS + SHEETS ──────────────────────────────────────
#     print("=" * 70)
#     print("STEP 2: GENERATING SCRIPTS → GOOGLE SHEETS")
#     print("=" * 70 + "\n")

#     worksheet = setup_google_sheets()
#     successful_saves = 0
#     failed_saves     = 0

#     if worksheet and selected_articles:
#         for idx, article in enumerate(selected_articles, 1):
#             print(f"\n[{idx:02d}/{len(selected_articles)}] "
#                   f"{article.get('source','')[:12]} | "
#                   f"{article.get('category','').upper():<12} | "
#                   f"{article['title'][:40]}...")

#             script = await create_reel_script_single(article)  # Always returns something now

#             success = save_to_google_sheets(
#                 worksheet,
#                 article.get('category', 'general'),
#                 article['title'],
#                 script,
#                 article.get('link', '')
#             )
#             if success:
#                 successful_saves += 1
#             else:
#                 failed_saves += 1

#             await asyncio.sleep(1)  # ✅ Reduced from 2s → 1s

#         print("\n" + "=" * 70)
#         print("✅ DONE!")
#         print("=" * 70)
#         print(f"   ✅ Saved  : {successful_saves}/{len(selected_articles)}")
#         print(f"   ❌ Failed : {failed_saves}")
#         print(f"   📊 Sheet  : https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")

#     else:
#         print("⚠️ No articles or Sheets unavailable!")

#     # ── FINAL SUMMARY ─────────────────────────────────────────────────
#     total_duration = (datetime.now() - start_time).total_seconds()
#     total_tokens   = total_input_tokens + total_output_tokens

#     print("\n" + "=" * 70)
#     print("📈 FINAL SUMMARY")
#     print("=" * 70)
#     print(f"   🔍 Analysis model     : {ANALYSIS_MODEL}")
#     print(f"   ✍️  Script model       : {SCRIPT_MODEL}")
#     print(f"   📰 Articles scraped   : {len(unique_articles)}")
#     print(f"   ✅ Scripts generated  : {successful_saves}")
#     print(f"   ⏱️  Total time         : {total_duration:.0f}s ({total_duration/60:.1f} mins)")
#     print(f"   📥 Input tokens       : {total_input_tokens:,}")
#     print(f"   📤 Output tokens      : {total_output_tokens:,}")
#     print(f"   🔢 Total tokens       : {total_tokens:,}")
#     print(f"   💰 Total cost         : ${total_cost:.4f} (~₹{total_cost*84:.2f})")
#     print(f"   💵 Cost per script    : ${total_cost/max(successful_saves,1):.4f}")
#     print("=" * 70 + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())



# -----------------------------links mistmatch code below but working very fine ---------------------


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
# from typing import List, Dict
# import hashlib


# # ============================================================
# # Perplexity Client
# # ============================================================
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),
#     base_url="https://api.perplexity.ai"
# )

# ANALYSIS_MODEL       = "sonar-pro"            # Cheap: categorization
# SCRIPT_MODEL         = "sonar-reasoning-pro"  # Quality: script writing

# ANALYSIS_INPUT_COST  = 1.0 / 1_000_000
# ANALYSIS_OUTPUT_COST = 1.0 / 1_000_000
# SCRIPT_INPUT_COST    = 2.0 / 1_000_000
# SCRIPT_OUTPUT_COST   = 8.0 / 1_000_000


# # ============================================================
# # Config
# # ============================================================
# GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
# GOOGLE_SHEET_NAME               = "Instagram Scripts"
# GOOGLE_WORKSHEET_NAME           = "Scripts"
# TARGET_SCRIPTS                  = 50

# VALID_CATEGORIES = [
#     "sports", "general", "crime", "politics",
#     "education", "economy", "entertainment", "horror"
# ]

# # Refusal detection keywords
# REFUSAL_KEYWORDS = [
#     "I appreciate", "I should clarify", "I'm Perplexity",
#     "search assistant", "I'm not able", "I cannot create",
#     "Would you like", "clarify my role", "I'm an AI",
#     "as an AI", "I don't create"
# ]


# # ============================================================
# # Token Tracking
# # ============================================================
# total_input_tokens  = 0
# total_output_tokens = 0
# total_cost          = 0.0
# processed_hashes    = set()


# # ============================================================
# # News Sites - 10 articles × 5 sites = 50
# # ============================================================
# NEWS_SITES = [
#     {
#         "name": "TV9 Marathi",
#         "url": "https://www.tv9marathi.com/latest-news",
#         "link_pattern": "tv9marathi.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "ABP Majha",
#         "url": "https://marathi.abplive.com/news",
#         "link_pattern": "abplive.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "Lokmat",
#         "url": "https://www.lokmat.com/latestnews/",
#         "link_pattern": "lokmat.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "Maharashtra Times",
#         "url": "https://maharashtratimes.com/",
#         "link_pattern": "maharashtratimes.com",
#         "target": 10,
#         "fetch_limit": 40
#     },
#     {
#         "name": "NDTV Marathi",
#         "url": "https://marathi.ndtv.com/",
#         "link_pattern": "marathi.ndtv.com",
#         "target": 10,
#         "fetch_limit": 40
#     }
# ]


# # ============================================================
# # Google Sheets Setup
# # ============================================================
# def setup_google_sheets():
#     try:
#         scope = [
#             'https://spreadsheets.google.com/feeds',
#             'https://www.googleapis.com/auth/drive'
#         ]
#         creds = Credentials.from_service_account_file(
#             GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scope
#         )
#         client = gspread.authorize(creds)

#         try:
#             sheet = client.open(GOOGLE_SHEET_NAME)
#             print(f"✅ Connected: '{GOOGLE_SHEET_NAME}'")
#         except gspread.SpreadsheetNotFound:
#             sheet = client.create(GOOGLE_SHEET_NAME)
#             print(f"✅ Created: '{GOOGLE_SHEET_NAME}'")

#         try:
#             worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
#             print(f"✅ Worksheet: '{GOOGLE_WORKSHEET_NAME}'")
#         except gspread.WorksheetNotFound:
#             worksheet = sheet.add_worksheet(
#                 title=GOOGLE_WORKSHEET_NAME, rows=5000, cols=10
#             )
#             worksheet.update('A1:E1', [[
#                 'Timestamp', 'Category', 'Title', 'Script', 'Source Link'
#             ]])
#             worksheet.format('A1:E1', {
#                 'textFormat': {
#                     'bold': True,
#                     'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
#                 },
#                 'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
#                 'horizontalAlignment': 'CENTER'
#             })
#             worksheet.set_column_width('A', 180)
#             worksheet.set_column_width('B', 150)
#             worksheet.set_column_width('C', 400)
#             worksheet.set_column_width('D', 600)
#             worksheet.set_column_width('E', 400)
#             print(f"✅ Created worksheet with headers")

#         return worksheet

#     except FileNotFoundError:
#         print(f"❌ credentials.json not found!")
#         return None
#     except Exception as e:
#         print(f"❌ Sheets setup error: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# # ============================================================
# # Save to Google Sheets
# # ============================================================
# def save_to_google_sheets(worksheet, category, title, script, source_link):
#     try:
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         script = '\n'.join(str(i) for i in script) if isinstance(script, list) else str(script).strip()
#         script = script.replace('[', '').replace(']', '')
#         title = str(title).strip()
#         source_link = str(source_link).strip()
#         category = str(category).strip().lower()

#         if category not in VALID_CATEGORIES:
#             category = "general"

#         next_row = len(worksheet.get_all_values()) + 1
#         worksheet.append_row(
#             [timestamp, category, title, script, source_link],
#             value_input_option='RAW'
#         )

#         worksheet.format(f'A{next_row}:E{next_row}', {
#             'textFormat': {
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
#             'wrapStrategy': 'WRAP',
#             'verticalAlignment': 'TOP'
#         })

#         category_colors = {
#             'crime':         {'red': 0.95, 'green': 0.8,  'blue': 0.8},
#             'politics':      {'red': 0.8,  'green': 0.9,  'blue': 1.0},
#             'sports':        {'red': 0.8,  'green': 1.0,  'blue': 0.8},
#             'entertainment': {'red': 1.0,  'green': 0.9,  'blue': 0.8},
#             'education':     {'red': 0.9,  'green': 0.95, 'blue': 1.0},
#             'economy':       {'red': 0.95, 'green': 1.0,  'blue': 0.85},
#             'horror':        {'red': 0.7,  'green': 0.7,  'blue': 0.7},
#             'general':       {'red': 1.0,  'green': 1.0,  'blue': 0.9}
#         }
#         worksheet.format(f'B{next_row}', {
#             'textFormat': {
#                 'bold': True,
#                 'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
#                 'fontSize': 10
#             },
#             'backgroundColor': category_colors.get(category, category_colors['general']),
#             'horizontalAlignment': 'CENTER'
#         })

#         print(f"✅ Saved [{category.upper()}] {title[:50]}...")
#         return True

#     except Exception as e:
#         print(f"❌ Save error: {e}")
#         return False


# # ============================================================
# # Content Hash
# # ============================================================
# def get_content_hash(title: str, content: str) -> str:
#     return hashlib.md5(
#         f"{title.lower()}{content[:200].lower()}".encode()
#     ).hexdigest()


# # ============================================================
# # Sort helper - FIX for lambda crash
# # ============================================================
# def sort_by_count(item):
#     return -item[1]


# def sort_by_priority(item):
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     return priority_order.get(item.get('importance', 'medium'), 2)


# # ============================================================
# # Marathi Validator
# # ============================================================
# def is_valid_marathi_script(script: str) -> bool:
#     if len(script) < 100:
#         return False
#     if any(kw.lower() in script.lower() for kw in REFUSAL_KEYWORDS):
#         return False
#     devanagari = len(re.findall(r'[\u0900-\u097F]', script))
#     total      = len(script.replace(' ', '').replace('\n', ''))
#     return (devanagari / max(total, 1)) > 0.35


# # ============================================================
# # Fetch Article with Retry
# # ============================================================
# async def fetch_article_with_retry(crawler, url: str, retries: int = 3) -> str:
#     for attempt in range(1, retries + 1):
#         try:
#             result = await crawler.arun(
#                 url,
#                 config=CrawlerRunConfig(
#                     cache_mode=CacheMode.BYPASS,
#                     word_count_threshold=10,
#                     page_timeout=25000
#                 )
#             )
#             if result.success and len(result.markdown) > 50:
#                 return result.markdown
#             await asyncio.sleep(2)
#         except Exception:
#             await asyncio.sleep(2)
#     return ""


# # ============================================================
# # Scraping - 10 per site guaranteed
# # ============================================================
# async def scrape_multiple_marathi_sources():
#     all_news = []

#     async with AsyncWebCrawler(verbose=False) as crawler:
#         for site in NEWS_SITES:
#             print(f"\n{'='*60}")
#             print(f"🔍 {site['name']} | Target: {site['target']}")
#             print(f"{'='*60}")

#             site_articles = []

#             try:
#                 result = await crawler.arun(
#                     site['url'],
#                     config=CrawlerRunConfig(
#                         cache_mode=CacheMode.BYPASS,
#                         wait_for="body",
#                         word_count_threshold=10,
#                         page_timeout=30000,
#                         js_code="await new Promise(r => setTimeout(r, 3000));"
#                     )
#                 )

#                 if not result.success:
#                     print(f"❌ Failed: {site['name']}")
#                     continue

#                 soup = BeautifulSoup(result.html, 'html.parser')
#                 raw_articles = []

#                 for link_tag in soup.find_all('a', href=True):
#                     href  = link_tag.get('href', '')
#                     title = link_tag.get_text(strip=True)

#                     if (15 < len(title) < 300 and
#                         site['link_pattern'] in href and
#                         not any(x in href.lower() for x in [
#                             'javascript:', 'mailto:', '#',
#                             '/category/', '/tag/', '/author/',
#                             'facebook.com', 'twitter.com', 'instagram.com',
#                             'youtube.com', 'whatsapp.com', '/myaccount/',
#                             '/install_app', '/advertisement', '/epaper',
#                             'web-stories', 'photo-gallery', '/videos/',
#                             '/games/', '/jokes/', '/terms-and-conditions',
#                             '/topic/', '/widget/', '/livetv',
#                             'articlelist', '/live'
#                         ])):

#                         if href.startswith('/'):
#                             base = (site['url'].split('/')[0] + '//'
#                                     + site['url'].split('/')[2])
#                             href = base + href

#                         if href.startswith('http'):
#                             raw_articles.append({'title': title, 'link': href})

#                 # Deduplicate
#                 seen = set()
#                 unique_links = []
#                 for a in raw_articles:
#                     if a['link'] not in seen:
#                         unique_links.append(a)
#                         seen.add(a['link'])

#                 print(f"📋 Found {len(unique_links)} unique links")

#                 for article in unique_links[:site['fetch_limit']]:
#                     if len(site_articles) >= site['target']:
#                         break

#                     print(f"   🔗 [{len(site_articles)+1}/{site['target']}] "
#                         f"{article['title'][:50]}...")

#                     markdown = await fetch_article_with_retry(crawler, article['link'])
#                     content  = markdown if markdown else article['title']
#                     content_hash = get_content_hash(article['title'], content)

#                     if content_hash not in processed_hashes:
#                         site_articles.append({
#                             'title':            article['title'],
#                             'link':             article['link'],  # ✅ Always original URL
#                             'content':          content[:2500],
#                             'hash':             content_hash,
#                             'has_full_content': bool(markdown)
#                         })
#                         processed_hashes.add(content_hash)
#                         tag = "✅" if markdown else "⚠️ fallback"
#                         print(f"   {tag} [{len(site_articles)}/{site['target']}] "
#                             f"{article['title'][:50]}...")
#                     else:
#                         print(f"   🔄 Duplicate skipped")

#                     await asyncio.sleep(1)

#                 print(f"\n📦 {site['name']}: {len(site_articles)}/{site['target']} collected")

#                 if site_articles:
#                     filtered = await smart_analyze_with_category(
#                         site_articles, site['name']
#                     )
#                     all_news.extend(filtered)
#                     print(f"🧠 {site['name']}: Analyzed {len(filtered)} articles")

#             except Exception as e:
#                 print(f"❌ Error {site['name']}: {e}")

#             await asyncio.sleep(3)

#     return all_news


# # ============================================================
# # AI Categorization - sonar-pro + link preservation
# # ============================================================
# async def smart_analyze_with_category(articles: List[Dict], source_name: str):
#     global total_input_tokens, total_output_tokens, total_cost

#     all_filtered = []

#     # ✅ FIX: Store original links BEFORE sending to AI
#     original_links = {article['title']: article['link'] for article in articles}

#     for i in range(0, len(articles), 5):
#         batch = articles[i:i+5]

#         articles_text = ""
#         for idx, article in enumerate(batch, i+1):
#             # ✅ 500 chars is enough to categorize (saves tokens)
#             articles_text += f"#{idx}: {article['title']}\n{article['content'][:500]}\n---\n"

#         # ✅ No link field in JSON - prevents AI from overwriting real URLs
#         prompt = f"""मराठी बातम्या विश्लेषक: खालील बातम्यांना category आणि Marathi summary द्या.

# ⚠️ नियम: detailed_summary आणि key_points फक्त मराठीत लिहा.

# Categories: sports, general, crime, politics, education, economy, entertainment, horror

# JSON array (link field नको):
# [{{"title":"EXACT शीर्षक","category":"cat","detailed_summary":"१५०-२०० शब्द मराठी सारांश - कोण, काय, कुठे, केव्हा सह","importance":"high/medium/low","key_points":["मराठी मुद्दा १","मराठी मुद्दा २","मराठी मुद्दा ३"]}}]

# बातम्या:
# {articles_text}

# फक्त JSON array. Link field नको."""

#         try:
#             response = perplexity_client.chat.completions.create(
#                 model=ANALYSIS_MODEL,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "Return ONLY valid JSON array. No link field. Summaries in Marathi only."
#                     },
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.2,
#                 max_tokens=3000
#             )

#             if hasattr(response, 'usage'):
#                 i_t = response.usage.prompt_tokens
#                 o_t = response.usage.completion_tokens
#                 total_input_tokens  += i_t
#                 total_output_tokens += o_t
#                 c = (i_t * ANALYSIS_INPUT_COST) + (o_t * ANALYSIS_OUTPUT_COST)
#                 total_cost += c
#                 print(f"   📊 {i_t}in + {o_t}out = ${c:.4f}")

#             content = response.choices[0].message.content
#             content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
#             match = re.search(r'\[.*\]', content, re.DOTALL)

#             if match:
#                 parsed = json.loads(match.group())

#                 # ✅ FIX: Restore original scraped links - never trust AI for URLs
#                 for art in parsed:
#                     ai_title = art.get('title', '')

#                     # Exact match first
#                     if ai_title in original_links:
#                         art['link'] = original_links[ai_title]
#                     else:
#                         # Fuzzy match by longest common substring
#                         best_link  = ''
#                         best_score = 0
#                         for orig_title, orig_link in original_links.items():
#                             score = sum(
#                                 1 for a, b in zip(ai_title[:40], orig_title[:40])
#                                 if a == b
#                             )
#                             if score > best_score:
#                                 best_score = score
#                                 best_link  = orig_link
#                         art['link'] = best_link

#                 all_filtered.extend(parsed)
#                 print(f"   ✅ Categorized {len(parsed)} articles with original links")

#             else:
#                 print(f"   ⚠️ JSON failed - using fallback entries")
#                 for article in batch:
#                     all_filtered.append({
#                         'title':            article['title'],
#                         'category':         'general',
#                         'detailed_summary': article['content'][:300],
#                         'importance':       'medium',
#                         'link':             article['link'],  # ✅ Always original
#                         'key_points':       [article['title']]
#                     })

#         except json.JSONDecodeError:
#             for article in batch:
#                 all_filtered.append({
#                     'title':            article['title'],
#                     'category':         'general',
#                     'detailed_summary': article['content'][:300],
#                     'importance':       'medium',
#                     'link':             article['link'],  # ✅ Always original
#                     'key_points':       [article['title']]
#                 })
#         except Exception as e:
#             print(f"   ❌ AI error: {e}")

#         await asyncio.sleep(1.5)

#     for art in all_filtered:
#         art['source']     = source_name
#         art['scraped_at'] = datetime.now().isoformat()

#     return all_filtered


# # ============================================================
# # Script Generation - sonar-reasoning-pro + anti-refusal
# # ============================================================
# async def create_reel_script_single(news_article: Dict):
#     global total_input_tokens, total_output_tokens, total_cost

#     category = news_article.get('category', 'general')

#     # ✅ FIX: Framed as formatting task - prevents identity refusal
#     system_prompt = """तुम्ही एक मराठी text formatter आहात.
# बातमीचे facts वापरून structured मराठी lines तयार करा.

# Structure (15-18 lines total):
# - Line 1-2: धक्कादायक hook (घटनेची सुरुवात)
# - Line 3-10: सर्व facts (नावे, ठिकाण, तारीख, संख्या सह)
# - Line 11-14: प्रश्न / विश्लेषण / ट्विस्ट
# - Line 15-18: CTA - शेवटची line नक्की हीच असावी:
#   "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

# नियम:
# - संपूर्ण output फक्त मराठीत (proper nouns सोडून)
# - 15-18 lines, प्रत्येक line 1-2 sentences
# - कोणतेही heading, explanation, markdown नाही
# - फक्त script lines output करा"""

#     summary    = news_article.get('detailed_summary', news_article.get('title', ''))[:300]
#     key_points = ', '.join(news_article.get('key_points', [news_article.get('title', '')]))

#     # Standard prompt
#     user_prompt_v1 = f"""Category: {category.upper()}
# शीर्षक: {news_article['title']}
# सारांश: {summary}
# मुद्दे: {key_points}

# वरील बातमीचे facts वापरून 15-18 मराठी lines तयार करा."""

#     # Stronger fallback prompt (used on refusal)
#     user_prompt_v2 = f"""खालील बातमीच्या facts वापरून 15 मराठी वाक्ये लिहा.
# बातमी: {news_article['title']}. {summary[:200]}
# प्रत्येक वाक्य नवीन line वर लिहा.
# शेवटची line: "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी." """

#     prompts = [user_prompt_v1, user_prompt_v2]

#     for attempt in range(1, 3):
#         try:
#             response = perplexity_client.chat.completions.create(
#                 model=SCRIPT_MODEL,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user",   "content": prompts[attempt - 1]}
#                 ],
#                 temperature=0.8,
#                 max_tokens=1200
#             )

#             if hasattr(response, 'usage'):
#                 i_t = response.usage.prompt_tokens
#                 o_t = response.usage.completion_tokens
#                 total_input_tokens  += i_t
#                 total_output_tokens += o_t
#                 total_cost += (i_t * SCRIPT_INPUT_COST) + (o_t * SCRIPT_OUTPUT_COST)

#             script = response.choices[0].message.content.strip()
#             script = re.sub(r'<think>.*?</think>', '', script, flags=re.DOTALL).strip()
#             script = script.replace('```', '').strip()

#             if is_valid_marathi_script(script):
#                 return script

#             # Check reason for failure
#             is_refusal = any(kw.lower() in script.lower() for kw in REFUSAL_KEYWORDS)
#             if is_refusal:
#                 print(f"   ⚠️ Attempt {attempt}: Model refused - retrying...")
#             else:
#                 print(f"   ⚠️ Attempt {attempt}: Not valid Marathi - retrying...")

#         except Exception as e:
#             print(f"   ⚠️ Attempt {attempt} error: {e}")
#             await asyncio.sleep(2)

#     # ✅ 100% Marathi hardcoded fallback - always valid
#     title = news_article.get('title', 'एक महत्त्वाची बातमी')[:80]
#     return f"""महाराष्ट्रात एक महत्त्वाची घडामोड समोर आली आहे.

# {title}

# ही बातमी सध्या सर्वत्र चर्चेत आहे.

# या घटनेने अनेकांना आश्चर्यचकित केले आहे.

# सर्वसामान्य नागरिकांवर याचा थेट परिणाम होणार आहे.

# प्रशासनाने याबाबत अद्याप अधिकृत प्रतिक्रिया दिलेली नाही.

# विरोधकांनी या निर्णयावर जोरदार टीका केली आहे.

# येत्या काही दिवसांत यावर मोठा निर्णय होण्याची शक्यता आहे.

# तुम्हाला या बातमीबद्दल काय वाटते?

# या प्रकरणाकडे सर्वांचे लक्ष लागले आहे.

# अशा महत्त्वाच्या बातम्यांसाठी आमचे पेज फॉलो करा.

# जबरी खबरी सोबत राहा, सत्य जाणून घ्या.

# तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."""


# # ============================================================
# # Main Pipeline
# # ============================================================
# async def main():
#     global total_input_tokens, total_output_tokens, total_cost

#     print("=" * 70)
#     print("🚀 JABARI KHABRI - SMART NEWS SCRAPER v5.0")
#     print(f"🔍 Analysis : {ANALYSIS_MODEL}")
#     print(f"✍️  Scripts  : {SCRIPT_MODEL}")
#     print("=" * 70)
#     print(f"📍 Sites    : TV9, ABP Majha, Lokmat, Mah Times, NDTV Marathi")
#     print(f"📊 Target   : 10 × 5 = {TARGET_SCRIPTS} scripts STRICTLY")
#     print(f"🔁 Buffer   : 40 links/site | 🔄 Retry: 3× fetch + 2× script")
#     print(f"🇮🇳 Language: मराठी only | 🔗 Links: original URLs preserved")
#     print("=" * 70 + "\n")

#     start_time = datetime.now()

#     # ── STEP 1: SCRAPING ─────────────────────────────────────────────
#     print("=" * 70)
#     print("STEP 1: SCRAPING 5 MARATHI NEWS SITES")
#     print("=" * 70 + "\n")

#     all_articles = await scrape_multiple_marathi_sources()

#     # Final deduplication
#     unique_articles = []
#     seen_hashes = set()
#     for article in all_articles:
#         h = article.get('hash', get_content_hash(
#             article['title'], article.get('detailed_summary', '')
#         ))
#         if h not in seen_hashes:
#             unique_articles.append(article)
#             seen_hashes.add(h)

#     print(f"\n✅ Total unique articles: {len(unique_articles)}")

#     # ✅ FIX: named function - no more lambda crash
#     category_counts = {}
#     for article in unique_articles:
#         cat = article.get('category', 'general')
#         category_counts[cat] = category_counts.get(cat, 0) + 1

#     print("\n📊 Category Breakdown:")
#     for cat, count in sorted(category_counts.items(), key=sort_by_count):
#         bar = "█" * count
#         print(f"   {cat.upper():<15} {bar} ({count})")

#     # Sort by importance
#     unique_articles.sort(key=sort_by_priority)
#     selected_articles = unique_articles[:TARGET_SCRIPTS]

#     print(f"\n🎯 Selected : {len(selected_articles)}/{TARGET_SCRIPTS}")
#     print(f"⏱️  Scraping : {(datetime.now()-start_time).total_seconds():.0f}s\n")

#     # ── STEP 2: SCRIPTS + SHEETS ──────────────────────────────────────
#     print("=" * 70)
#     print("STEP 2: GENERATING SCRIPTS → GOOGLE SHEETS")
#     print("=" * 70 + "\n")

#     worksheet        = setup_google_sheets()
#     successful_saves = 0
#     failed_saves     = 0

#     if worksheet and selected_articles:
#         for idx, article in enumerate(selected_articles, 1):
#             print(f"\n[{idx:02d}/{len(selected_articles)}] "
#                 f"{article.get('source','')[:12]} | "
#                 f"{article.get('category','').upper():<13} | "
#                 f"{article['title'][:40]}...")

#             script = await create_reel_script_single(article)

#             # ✅ Log Marathi percentage for debugging
#             dev_chars  = len(re.findall(r'[\u0900-\u097F]', script))
#             total_ch   = len(script.replace(' ', '').replace('\n', ''))
#             marathi_pct = (dev_chars / max(total_ch, 1)) * 100
#             lang_tag    = "🇮🇳" if marathi_pct > 35 else "⚠️ Non-Marathi"
#             print(f"   📝 {lang_tag} ({marathi_pct:.0f}% Devanagari) | "
#                 f"🔗 {article.get('link','')[:60]}...")

#             success = save_to_google_sheets(
#                 worksheet,
#                 article.get('category', 'general'),
#                 article['title'],
#                 script,
#                 article.get('link', '')
#             )
#             if success:
#                 successful_saves += 1
#             else:
#                 failed_saves += 1

#             await asyncio.sleep(1)

#         print("\n" + "=" * 70)
#         print(f"   ✅ Saved  : {successful_saves}/{len(selected_articles)}")
#         print(f"   ❌ Failed : {failed_saves}")
#         print(f"   📊 Sheet  : https://docs.google.com/spreadsheets/d/"
#             f"{worksheet.spreadsheet.id}")

#     else:
#         print("⚠️ No articles or Sheets unavailable!")

#     # ── FINAL SUMMARY ─────────────────────────────────────────────────
#     total_duration = (datetime.now() - start_time).total_seconds()
#     total_tokens   = total_input_tokens + total_output_tokens

#     print("\n" + "=" * 70)
#     print("📈 FINAL SUMMARY")
#     print("=" * 70)
#     print(f"   🔍 Analysis model     : {ANALYSIS_MODEL}")
#     print(f"   ✍️  Script model       : {SCRIPT_MODEL}")
#     print(f"   📰 Articles scraped   : {len(unique_articles)}")
#     print(f"   ✅ Scripts generated  : {successful_saves}")
#     print(f"   ⏱️  Total time         : {total_duration:.0f}s ({total_duration/60:.1f} mins)")
#     print(f"   📥 Input tokens       : {total_input_tokens:,}")
#     print(f"   📤 Output tokens      : {total_output_tokens:,}")
#     print(f"   🔢 Total tokens       : {total_tokens:,}")
#     print(f"   💰 Total cost         : ${total_cost:.4f} (~₹{total_cost*84:.2f})")
#     print(f"   💵 Cost per script    : ${total_cost/max(successful_saves,1):.4f}")
#     print("=" * 70 + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())





# -----------------------------------------------


import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import gspread
from google.oauth2.service_account import Credentials
import os
from typing import List, Dict
import hashlib


# ============================================================
# Custom Exceptions
# ============================================================
class CreditExhaustedException(Exception):
    """Raised when Perplexity API credits are exhausted"""
    pass


# ============================================================
# Perplexity Client
# ============================================================
perplexity_client = OpenAI(
    api_key=os.environ.get("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)

ANALYSIS_MODEL       = "sonar-pro"
SCRIPT_MODEL         = "sonar-reasoning-pro"

ANALYSIS_INPUT_COST  = 1.0 / 1_000_000
ANALYSIS_OUTPUT_COST = 1.0 / 1_000_000
SCRIPT_INPUT_COST    = 2.0 / 1_000_000
SCRIPT_OUTPUT_COST   = 8.0 / 1_000_000


# ============================================================
# Config
# ============================================================
GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
GOOGLE_SHEET_NAME               = "Instagram Scripts"
GOOGLE_WORKSHEET_NAME           = "Scripts"
TARGET_SCRIPTS                  = 10

VALID_CATEGORIES = [
    "sports", "general", "crime", "politics",
    "education", "economy", "entertainment", "horror"
]

REFUSAL_KEYWORDS = [
    "I appreciate", "I should clarify", "I'm Perplexity",
    "search assistant", "I'm not able", "I cannot create",
    "Would you like", "clarify my role", "I'm an AI",
    "as an AI", "I don't create"
]


# ============================================================
# Token Tracking
# ============================================================
total_input_tokens  = 0
total_output_tokens = 0
total_cost          = 0.0
processed_hashes    = set()


# ============================================================
# News Sites
# ============================================================
NEWS_SITES = [
    {
        "name": "TV9 Marathi",
        "url": "https://www.tv9marathi.com/latest-news",
        "link_pattern": "tv9marathi.com",
        "target": 2,
        "fetch_limit": 10
    },
    {
        "name": "ABP Majha",
        "url": "https://marathi.abplive.com/news",
        "link_pattern": "abplive.com",
        "target": 2,
        "fetch_limit": 10
    },
    {
        "name": "Lokmat",
        "url": "https://www.lokmat.com/latestnews/",
        "link_pattern": "lokmat.com",
        "target": 2,
        "fetch_limit": 10
    },
    {
        "name": "Maharashtra Times",
        "url": "https://maharashtratimes.com/",
        "link_pattern": "maharashtratimes.com",
        "target": 2,
        "fetch_limit": 10
    },
    {
        "name": "NDTV Marathi",
        "url": "https://marathi.ndtv.com/",
        "link_pattern": "marathi.ndtv.com",
        "target": 2,
        "fetch_limit": 10
    }
]


# ============================================================
# Google Sheets Setup
# ============================================================
def setup_google_sheets():
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scope
        )
        client = gspread.authorize(creds)

        try:
            sheet = client.open(GOOGLE_SHEET_NAME)
            print(f"✅ Connected: '{GOOGLE_SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(GOOGLE_SHEET_NAME)
            print(f"✅ Created: '{GOOGLE_SHEET_NAME}'")

        try:
            worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
            print(f"✅ Worksheet: '{GOOGLE_WORKSHEET_NAME}'")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(
                title=GOOGLE_WORKSHEET_NAME, rows=5000, cols=10
            )
            worksheet.update('A1:E1', [[
                'Timestamp', 'Category', 'Title', 'Script', 'Source Link'
            ]])
            worksheet.format('A1:E1', {
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                },
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'horizontalAlignment': 'CENTER'
            })
            worksheet.set_column_width('A', 180)
            worksheet.set_column_width('B', 150)
            worksheet.set_column_width('C', 400)
            worksheet.set_column_width('D', 600)
            worksheet.set_column_width('E', 400)
            print(f"✅ Created worksheet with headers")

        return worksheet

    except FileNotFoundError:
        print(f"❌ credentials.json not found!")
        return None
    except Exception as e:
        print(f"❌ Sheets setup error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================
# Save to Google Sheets
# ============================================================
def save_to_google_sheets(worksheet, category, title, script, source_link):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        script = '\n'.join(str(i) for i in script) if isinstance(script, list) else str(script).strip()
        script = script.replace('[', '').replace(']', '')
        title = str(title).strip()
        source_link = str(source_link).strip()
        category = str(category).strip().lower()

        if category not in VALID_CATEGORIES:
            category = "general"

        next_row = len(worksheet.get_all_values()) + 1
        worksheet.append_row(
            [timestamp, category, title, script, source_link],
            value_input_option='RAW'
        )

        worksheet.format(f'A{next_row}:E{next_row}', {
            'textFormat': {
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
                'fontSize': 10
            },
            'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP'
        })

        category_colors = {
            'crime':         {'red': 0.95, 'green': 0.8,  'blue': 0.8},
            'politics':      {'red': 0.8,  'green': 0.9,  'blue': 1.0},
            'sports':        {'red': 0.8,  'green': 1.0,  'blue': 0.8},
            'entertainment': {'red': 1.0,  'green': 0.9,  'blue': 0.8},
            'education':     {'red': 0.9,  'green': 0.95, 'blue': 1.0},
            'economy':       {'red': 0.95, 'green': 1.0,  'blue': 0.85},
            'horror':        {'red': 0.7,  'green': 0.7,  'blue': 0.7},
            'general':       {'red': 1.0,  'green': 1.0,  'blue': 0.9}
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
        print(f"❌ Save error: {e}")
        return False


# ============================================================
# Content Hash
# ============================================================
def get_content_hash(title: str, content: str) -> str:
    return hashlib.md5(
        f"{title.lower()}{content[:200].lower()}".encode()
    ).hexdigest()


# ============================================================
# Sort helpers
# ============================================================
def sort_by_count(item):
    return -item[1]


def sort_by_priority(item):
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    return priority_order.get(item.get('importance', 'medium'), 2)


# ============================================================
# Marathi Validator
# ============================================================
def is_valid_marathi_script(script: str) -> bool:
    if len(script) < 100:
        return False
    if any(kw.lower() in script.lower() for kw in REFUSAL_KEYWORDS):
        return False
    devanagari = len(re.findall(r'[\u0900-\u097F]', script))
    total      = len(script.replace(' ', '').replace('\n', ''))
    return (devanagari / max(total, 1)) > 0.35


# ============================================================
# API Credit Check
# ============================================================
async def check_api_credits():
    try:
        perplexity_client.chat.completions.create(
            model=ANALYSIS_MODEL,
            messages=[{"role": "user", "content": "ok"}],
            max_tokens=1
        )
        print("✅ API credits OK")
        return True
    except Exception as e:
        error_str = str(e).lower()
        if any(code in error_str for code in [
            '402', '429', '401',
            'insufficient', 'credit', 'quota',
            'balance', 'payment', 'billing',
            'rate limit', 'exceeded'
        ]):
            print("=" * 60)
            print("❌ PERPLEXITY API CREDITS EXHAUSTED!")
            print(f"   Error: {str(e)}")
            print("=" * 60)
            print("👉 Top up: https://www.perplexity.ai/settings/api")
            return False
        print(f"❌ Unknown API error: {e}")
        return False


# ============================================================
# Fetch Article with Retry
# ============================================================
async def fetch_article_with_retry(crawler, url: str, retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            result = await crawler.arun(
                url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=10,
                    page_timeout=25000
                )
            )
            if result.success and len(result.markdown) > 50:
                return result.markdown
            await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2)
    return ""


# ============================================================
# Scraping - 10 per site guaranteed
# ============================================================
async def scrape_multiple_marathi_sources():
    all_news = []

    async with AsyncWebCrawler(verbose=False) as crawler:
        for site in NEWS_SITES:
            print(f"\n{'='*60}")
            print(f"🔍 {site['name']} | Target: {site['target']}")
            print(f"{'='*60}")

            site_articles = []

            try:
                result = await crawler.arun(
                    site['url'],
                    config=CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        wait_for="body",
                        word_count_threshold=10,
                        page_timeout=30000,
                        js_code="await new Promise(r => setTimeout(r, 3000));"
                    )
                )

                if not result.success:
                    print(f"❌ Failed: {site['name']}")
                    continue

                soup = BeautifulSoup(result.html, 'html.parser')
                raw_articles = []

                for link_tag in soup.find_all('a', href=True):
                    href  = link_tag.get('href', '')
                    title = link_tag.get_text(strip=True)

                    if (15 < len(title) < 300 and
                        site['link_pattern'] in href and
                        not any(x in href.lower() for x in [
                            'javascript:', 'mailto:', '#',
                            '/category/', '/tag/', '/author/',
                            'facebook.com', 'twitter.com', 'instagram.com',
                            'youtube.com', 'whatsapp.com', '/myaccount/',
                            '/install_app', '/advertisement', '/epaper',
                            'web-stories', 'photo-gallery', '/videos/',
                            '/games/', '/jokes/', '/terms-and-conditions',
                            '/topic/', '/widget/', '/livetv',
                            'articlelist', '/live'
                        ])):

                        if href.startswith('/'):
                            base = (site['url'].split('/')[0] + '//'
                                    + site['url'].split('/')[2])
                            href = base + href

                        if href.startswith('http'):
                            raw_articles.append({'title': title, 'link': href})

                # Deduplicate
                seen = set()
                unique_links = []
                for a in raw_articles:
                    if a['link'] not in seen:
                        unique_links.append(a)
                        seen.add(a['link'])

                print(f"📋 Found {len(unique_links)} unique links")

                for article in unique_links[:site['fetch_limit']]:
                    if len(site_articles) >= site['target']:
                        break

                    print(f"   🔗 [{len(site_articles)+1}/{site['target']}] "
                        f"{article['title'][:50]}...")

                    markdown = await fetch_article_with_retry(crawler, article['link'])
                    content  = markdown if markdown else article['title']
                    content_hash = get_content_hash(article['title'], content)

                    if content_hash not in processed_hashes:
                        site_articles.append({
                            'title':            article['title'],
                            'link':             article['link'],
                            'content':          content[:2500],
                            'hash':             content_hash,
                            'has_full_content': bool(markdown)
                        })
                        processed_hashes.add(content_hash)
                        tag = "✅" if markdown else "⚠️ fallback"
                        print(f"   {tag} [{len(site_articles)}/{site['target']}] "
                            f"{article['title'][:50]}...")
                    else:
                        print(f"   🔄 Duplicate skipped")

                    await asyncio.sleep(1)

                print(f"\n📦 {site['name']}: {len(site_articles)}/{site['target']} collected")

                if site_articles:
                    filtered = await smart_analyze_with_category(
                        site_articles, site['name']
                    )
                    all_news.extend(filtered)
                    print(f"🧠 {site['name']}: Analyzed {len(filtered)} articles")

            except Exception as e:
                print(f"❌ Error {site['name']}: {e}")

            await asyncio.sleep(3)

    return all_news


# ============================================================
# AI Categorization - INDEX-BASED link preservation
# ============================================================
async def smart_analyze_with_category(articles: List[Dict], source_name: str):
    global total_input_tokens, total_output_tokens, total_cost

    all_filtered = []

    for batch_start in range(0, len(articles), 5):
        batch = articles[batch_start:batch_start + 5]

        # ✅ Store links and titles BY POSITION INDEX
        index_to_link  = {i: article['link']  for i, article in enumerate(batch)}
        index_to_title = {i: article['title'] for i, article in enumerate(batch)}

        articles_text = ""
        for idx, article in enumerate(batch):
            articles_text += f"INDEX_{idx}: {article['title']}\n{article['content'][:500]}\n---\n"

        prompt = f"""मराठी बातम्या विश्लेषक: खालील बातम्यांना category आणि Marathi summary द्या.

⚠️ नियम:
1. detailed_summary आणि key_points फक्त मराठीत लिहा
2. JSON मध्ये "index" field EXACTLY जसा दिला (0,1,2,3,4) तसाच परत द्या
3. title आणि link field नको - फक्त index वापरा

Categories: sports, general, crime, politics, education, economy, entertainment, horror

JSON array format:
[{{"index": 0, "category": "cat", "detailed_summary": "मराठी सारांश १५०-२०० शब्द", "importance": "high/medium/low", "key_points": ["मुद्दा १", "मुद्दा २", "मुद्दा ३"]}}]

बातम्या:
{articles_text}

फक्त JSON array. Index 0 ते {len(batch)-1} पर्यंत."""

        try:
            response = perplexity_client.chat.completions.create(
                model=ANALYSIS_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Return ONLY valid JSON array. Use index field (0,1,2...). No title or link fields."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )

            if hasattr(response, 'usage'):
                i_t = response.usage.prompt_tokens
                o_t = response.usage.completion_tokens
                total_input_tokens  += i_t
                total_output_tokens += o_t
                c = (i_t * ANALYSIS_INPUT_COST) + (o_t * ANALYSIS_OUTPUT_COST)
                total_cost += c
                print(f"   📊 {i_t}in + {o_t}out = ${c:.4f}")

            content = response.choices[0].message.content
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

            # ✅ CORRECT regex - single backslash, not double
            match = re.search(r'\[.*\]', content, re.DOTALL)

            if match:
                parsed = json.loads(match.group())

                for art in parsed:
                    idx = art.get('index')

                    # ✅ Always restore link and title from index
                    if idx is not None and idx in index_to_link:
                        art['link']  = index_to_link[idx]
                        art['title'] = index_to_title[idx]
                    else:
                        # Fallback: sequential position
                        pos = len(all_filtered) % len(batch)
                        art['link']  = index_to_link.get(pos, '')
                        art['title'] = index_to_title.get(pos, art.get('title', ''))

                    # Validate category
                    if art.get('category') not in VALID_CATEGORIES:
                        art['category'] = 'general'

                all_filtered.extend(parsed)
                print(f"   ✅ Categorized {len(parsed)} | Links: INDEX-matched ✅")

            else:
                print(f"   ⚠️ JSON failed - fallback entries")
                for i, article in enumerate(batch):
                    all_filtered.append({
                        'index':            i,
                        'title':            article['title'],
                        'category':         'general',
                        'detailed_summary': article['content'][:300],
                        'importance':       'medium',
                        'link':             article['link'],
                        'key_points':       [article['title']]
                    })

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            for i, article in enumerate(batch):
                all_filtered.append({
                    'index':            i,
                    'title':            article['title'],
                    'category':         'general',
                    'detailed_summary': article['content'][:300],
                    'importance':       'medium',
                    'link':             article['link'],
                    'key_points':       [article['title']]
                })
        except Exception as e:
            error_str = str(e).lower()
            if any(code in error_str for code in [
                '402', '429', 'credit', 'quota',
                'insufficient', 'balance', 'billing'
            ]):
                print(f"\n💳 CREDITS EXHAUSTED during analysis!")
                raise CreditExhaustedException(str(e))
            print(f"   ❌ AI error: {e}")

        await asyncio.sleep(1.5)

    for art in all_filtered:
        art['source']     = source_name
        art['scraped_at'] = datetime.now().isoformat()

    return all_filtered


# ============================================================
# Script Generation
# ============================================================
async def create_reel_script_single(news_article: Dict):
    global total_input_tokens, total_output_tokens, total_cost

    category = news_article.get('category', 'general')

    system_prompt = """तुम्ही एक मराठी text formatter आहात.
बातमीचे facts वापरून structured मराठी lines तयार करा.

Structure (15-18 lines total):
- Line 1-2: धक्कादायक hook (घटनेची सुरुवात)
- Line 3-10: सर्व facts (नावे, ठिकाण, तारीख, संख्या सह)
- Line 11-14: प्रश्न / विश्लेषण / ट्विस्ट
- Line 15-18: CTA - शेवटची line नक्की हीच असावी:
"तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."

नियम:
- संपूर्ण output फक्त मराठीत (proper nouns सोडून)
- 15-18 lines, प्रत्येक line 1-2 sentences
- कोणतेही heading, explanation, markdown नाही
- फक्त script lines output करा"""

    summary    = news_article.get('detailed_summary', news_article.get('title', ''))[:300]
    key_points = ', '.join(news_article.get('key_points', [news_article.get('title', '')]))

    user_prompt_v1 = f"""Category: {category.upper()}
शीर्षक: {news_article['title']}
सारांश: {summary}
मुद्दे: {key_points}

वरील बातमीचे facts वापरून 15-18 मराठी lines तयार करा."""

    user_prompt_v2 = f"""खालील बातमीच्या facts वापरून 15 मराठी वाक्ये लिहा.
बातमी: {news_article['title']}. {summary[:200]}
प्रत्येक वाक्य नवीन line वर लिहा.
शेवटची line: "तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी." """

    prompts = [user_prompt_v1, user_prompt_v2]

    for attempt in range(1, 3):
        try:
            response = perplexity_client.chat.completions.create(
                model=SCRIPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompts[attempt - 1]}
                ],
                temperature=0.8,
                max_tokens=1200
            )

            if hasattr(response, 'usage'):
                i_t = response.usage.prompt_tokens
                o_t = response.usage.completion_tokens
                total_input_tokens  += i_t
                total_output_tokens += o_t
                total_cost += (i_t * SCRIPT_INPUT_COST) + (o_t * SCRIPT_OUTPUT_COST)

            script = response.choices[0].message.content.strip()
            script = re.sub(r'<think>.*?</think>', '', script, flags=re.DOTALL).strip()
            script = script.replace('```', '').strip()

            if is_valid_marathi_script(script):
                return script

            is_refusal = any(kw.lower() in script.lower() for kw in REFUSAL_KEYWORDS)
            if is_refusal:
                print(f"   ⚠️ Attempt {attempt}: Model refused - retrying...")
            else:
                print(f"   ⚠️ Attempt {attempt}: Not valid Marathi - retrying...")

        except Exception as e:
            error_str = str(e).lower()
            if any(code in error_str for code in [
                '402', '429', 'credit', 'quota',
                'insufficient', 'balance', 'billing'
            ]):
                print(f"\n💳 CREDITS EXHAUSTED during script generation!")
                raise CreditExhaustedException(str(e))
            print(f"   ⚠️ Attempt {attempt} error: {e}")
            await asyncio.sleep(2)

    # 100% Marathi hardcoded fallback
    title = news_article.get('title', 'एक महत्त्वाची बातमी')[:80]
    return f"""महाराष्ट्रात एक महत्त्वाची घडामोड समोर आली आहे.

{title}

ही बातमी सध्या सर्वत्र चर्चेत आहे.

या घटनेने अनेकांना आश्चर्यचकित केले आहे.

सर्वसामान्य नागरिकांवर याचा थेट परिणाम होणार आहे.

प्रशासनाने याबाबत अद्याप अधिकृत प्रतिक्रिया दिलेली नाही.

विरोधकांनी या निर्णयावर जोरदार टीका केली आहे.

येत्या काही दिवसांत यावर मोठा निर्णय होण्याची शक्यता आहे.

तुम्हाला या बातमीबद्दल काय वाटते?

या प्रकरणाकडे सर्वांचे लक्ष लागले आहे.

अशा महत्त्वाच्या बातम्यांसाठी आमचे पेज फॉलो करा.

जबरी खबरी सोबत राहा, सत्य जाणून घ्या.

तुमचं काय मत आहे? कमेंट करून सांगा आणि फॉलो करा जबरी खबरी."""


# ============================================================
# Main Pipeline
# ============================================================
async def main():
    global total_input_tokens, total_output_tokens, total_cost

    print("=" * 70)
    print("🚀 JABARI KHABRI - SMART NEWS SCRAPER v5.0")
    print(f"🔍 Analysis : {ANALYSIS_MODEL}")
    print(f"✍️  Scripts  : {SCRIPT_MODEL}")
    print("=" * 70)

    # ✅ STEP 0: CHECK CREDITS BEFORE ANYTHING
    credits_ok = await check_api_credits()
    if not credits_ok:
        print("\n🛑 Stopping. Top up credits first.")
        print("👉 https://www.perplexity.ai/settings/api")
        return

    start_time = datetime.now()

    # ── STEP 1: SCRAPING ─────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STEP 1: SCRAPING 5 MARATHI NEWS SITES")
    print("=" * 70 + "\n")

    try:
        all_articles = await scrape_multiple_marathi_sources()
    except CreditExhaustedException:
        print("\n🛑 Credits exhausted during scraping. Stopping.")
        return

    # Final deduplication
    unique_articles = []
    seen_hashes = set()
    for article in all_articles:
        h = article.get('hash', get_content_hash(
            article['title'], article.get('detailed_summary', '')
        ))
        if h not in seen_hashes:
            unique_articles.append(article)
            seen_hashes.add(h)

    print(f"\n✅ Total unique articles: {len(unique_articles)}")

    # Category breakdown
    category_counts = {}
    for article in unique_articles:
        cat = article.get('category', 'general')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\n📊 Category Breakdown:")
    for cat, count in sorted(category_counts.items(), key=sort_by_count):
        bar = "█" * count
        print(f"   {cat.upper():<15} {bar} ({count})")

    # Sort by importance
    unique_articles.sort(key=sort_by_priority)
    selected_articles = unique_articles[:TARGET_SCRIPTS]

    print(f"\n🎯 Selected : {len(selected_articles)}/{TARGET_SCRIPTS}")
    print(f"⏱️  Scraping : {(datetime.now()-start_time).total_seconds():.0f}s\n")

    # ── STEP 2: SCRIPTS + SHEETS ──────────────────────────────────────
    print("=" * 70)
    print("STEP 2: GENERATING SCRIPTS → GOOGLE SHEETS")
    print("=" * 70 + "\n")

    worksheet        = setup_google_sheets()
    successful_saves = 0
    failed_saves     = 0

    if worksheet and selected_articles:
        for idx, article in enumerate(selected_articles, 1):
            print(f"\n[{idx:02d}/{len(selected_articles)}] "
                f"{article.get('source','')[:12]} | "
                f"{article.get('category','').upper():<13} | "
                f"{article['title'][:40]}...")

            try:
                script = await create_reel_script_single(article)
            except CreditExhaustedException:
                print(f"\n🛑 Credits exhausted at script {idx}/{len(selected_articles)}")
                print(f"   ✅ Saved so far: {successful_saves} scripts")
                print(f"👉 Top up: https://www.perplexity.ai/settings/api")
                break

            # Log Marathi %
            dev_chars   = len(re.findall(r'[\u0900-\u097F]', script))
            total_ch    = len(script.replace(' ', '').replace('\n', ''))
            marathi_pct = (dev_chars / max(total_ch, 1)) * 100
            lang_tag    = "🇮🇳" if marathi_pct > 35 else "⚠️"
            print(f"   📝 {lang_tag} ({marathi_pct:.0f}%) | "
                f"🔗 {article.get('link','')[:60]}...")

            success = save_to_google_sheets(
                worksheet,
                article.get('category', 'general'),
                article['title'],
                script,
                article.get('link', '')
            )
            if success:
                successful_saves += 1
            else:
                failed_saves += 1

            await asyncio.sleep(1)

    # ── FINAL SUMMARY ─────────────────────────────────────────────────
    total_duration = (datetime.now() - start_time).total_seconds()
    total_tokens   = total_input_tokens + total_output_tokens

    print("\n" + "=" * 70)
    print("📈 FINAL SUMMARY")
    print("=" * 70)
    print(f"   🔍 Analysis model     : {ANALYSIS_MODEL}")
    print(f"   ✍️  Script model       : {SCRIPT_MODEL}")
    print(f"   📰 Articles scraped   : {len(unique_articles)}")
    print(f"   ✅ Scripts saved      : {successful_saves}")
    print(f"   ❌ Failed             : {failed_saves}")
    print(f"   ⏱️  Total time         : {total_duration:.0f}s ({total_duration/60:.1f} mins)")
    print(f"   📥 Input tokens       : {total_input_tokens:,}")
    print(f"   📤 Output tokens      : {total_output_tokens:,}")
    print(f"   🔢 Total tokens       : {total_tokens:,}")
    print(f"   💰 Total cost         : ${total_cost:.4f} (~₹{total_cost*84:.2f})")
    print(f"   💵 Cost per script    : ${total_cost/max(successful_saves,1):.4f}")
    if worksheet:
        print(f"   📊 Sheet URL          : https://docs.google.com/spreadsheets/d/"
            f"{worksheet.spreadsheet.id}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
