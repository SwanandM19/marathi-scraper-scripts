# import asyncio
# import json
# from datetime import datetime
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
# from bs4 import BeautifulSoup
# from openai import OpenAI
# import re
# import os

# # Initialize Perplexity client with environment variable
# perplexity_client = OpenAI(
#     api_key=os.environ.get("PERPLEXITY_API_KEY"),  # Read from GitHub Secrets
#     base_url="https://api.perplexity.ai"
# )

# # Track token usage (CORRECTED: $1 per 1M tokens)
# total_tokens_used = 0
# total_cost = 0.0

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
#                 # Step 1: Fetch homepage with JavaScript rendering
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
                    
#                     # Strategy: Find all links with Marathi text
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
#                         # Get top 12 articles per site
#                         print(f"📄 Fetching detailed content from top {min(12, len(unique_articles))} articles...")
                        
#                         articles_with_content = []
#                         for article in unique_articles[:12]:  # Top 12 per site
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
                        
#                         # Step 3: AI analysis
#                         if articles_with_content:
#                             filtered_news = await smart_analyze_with_detailed_summary(
#                                 articles_with_content, 
#                                 site['name']
#                             )
#                             all_news.extend(filtered_news)
#                             print(f"✅ Extracted {len(filtered_news)} important articles with detailed summaries")
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
#     AI analysis with CORRECTED token tracking ($1 per 1M tokens)
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

# **JSON format (फक्त array परत करा, इतर काही नाही):**
# [
#   {{
#     "title": "मूळ शीर्षक",
#     "category": "crime/politics/general",
#     "detailed_summary": "संपूर्ण विस्तृत सारांश 150-250 शब्दांत मराठीत. काय घडलं? कुठे? कधी? कोण आहेत? कोणती कारवाई? काय परिणाम? इतर तपशील समाविष्ट करा",
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
#                         "content": "You are an expert Marathi news analyst. Return ONLY valid JSON array. No markdown, no explanation, no extra text."
#                     },
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=0.3,
#                 max_tokens=4000
#             )
            
#             # Track tokens (CORRECTED: $1 per 1M tokens)
#             if hasattr(response, 'usage'):
#                 batch_tokens = response.usage.total_tokens
#                 total_tokens_used += batch_tokens
                
#                 # CORRECT pricing: $1 per 1M tokens
#                 batch_cost = (batch_tokens / 1_000_000) * 1.0
#                 total_cost += batch_cost
                
#                 print(f"   📊 Batch tokens: {batch_tokens:,} | Cost: ${batch_cost:.4f}")
            
#             content = response.choices[0].message.content
            
#             # Extract JSON
#             json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
#             if json_match:
#                 batch_articles = json.loads(json_match.group())
#                 all_filtered.extend(batch_articles)
#                 print(f"   ✅ Extracted {len(batch_articles)} articles from this batch")
#             else:
#                 print(f"   ⚠️ No valid JSON in AI response")
            
#         except json.JSONDecodeError as e:
#             print(f"   ❌ JSON parsing error: {e}")
#         except Exception as e:
#             print(f"   ❌ AI analysis error: {e}")
    
#     # Add source and timestamp
#     for article in all_filtered:
#         article['source'] = source_name
#         article['scraped_at'] = datetime.now().isoformat()
    
#     return all_filtered


# async def main():
#     global total_tokens_used, total_cost
    
#     print("🚀 Starting Smart Marathi News Scraper with DETAILED Summaries")
#     print("📍 Focus: Criminal, Political & Important General News")
#     print("📝 Feature: Detailed 150-250 word summaries")
#     print("💰 Token tracking enabled (Correct pricing: $1/1M tokens)")
#     print("🎯 Strategy: Get top 10 news from ALL THREE SITES COMBINED\n")
    
#     start_time = datetime.now()
    
#     # Scrape all sites
#     all_articles = await scrape_marathi_news_final()
    
#     # Remove duplicates by title
#     unique_articles = []
#     seen_titles = set()
    
#     for article in all_articles:
#         title_lower = article['title'].lower()
#         if title_lower not in seen_titles:
#             unique_articles.append(article)
#             seen_titles.add(title_lower)
    
#     # Sort ALL articles by importance FIRST
#     priority_order = {'high': 1, 'medium': 2, 'low': 3}
#     unique_articles.sort(key=lambda x: priority_order.get(x.get('importance', 'medium'), 2))
    
#     # Save ALL articles to JSON (fixed filename)
#     output_file = "latest_news.json"
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    
#     # Save TOP 10 to separate file (fixed filename)
#     top_10_articles = unique_articles[:10]
#     top_10_file = "top_10_latest.json"
#     with open(top_10_file, 'w', encoding='utf-8') as f:
#         json.dump(top_10_articles, f, ensure_ascii=False, indent=2)
    
#     end_time = datetime.now()
#     duration = (end_time - start_time).total_seconds()
    
#     # Final summary
#     print("\n" + "="*80)
#     print("📊 SCRAPING SUMMARY")
#     print("="*80)
#     print(f"   Total articles scraped: {len(unique_articles)}")
#     print(f"   High importance: {len([a for a in unique_articles if a.get('importance') == 'high'])}")
#     print(f"   Crime news: {len([a for a in unique_articles if a.get('category') == 'crime'])}")
#     print(f"   Political news: {len([a for a in unique_articles if a.get('category') == 'politics'])}")
#     print(f"   General news: {len([a for a in unique_articles if a.get('category') == 'general'])}")
#     print(f"\n   By source:")
#     for source in ['TV9 Marathi', 'ABP Majha', 'Lokmat']:
#         count = len([a for a in unique_articles if a['source'] == source])
#         count_top10 = len([a for a in top_10_articles if a['source'] == source])
#         print(f"      • {source}: {count} total articles | {count_top10} in TOP 10")
#     print(f"\n💾 All articles saved to: {output_file}")
#     print(f"🏆 TOP 10 articles saved to: {top_10_file}")
#     print(f"\n⏱️  Total time: {duration:.2f} seconds")
#     print(f"🔢 Total tokens used: {total_tokens_used:,}")
#     print(f"💰 Estimated cost: ${total_cost:.4f} (@ $1.00 per 1M tokens)")
#     if len(unique_articles) > 0:
#         print(f"📈 Average tokens per article: {total_tokens_used // len(unique_articles):,}")
#     print("="*80 + "\n")
    
#     # Display TOP 10 from ALL sites combined
#     if len(top_10_articles) > 0:
#         print("🏆 TOP 10 IMPORTANT NEWS FROM ALL THREE SITES COMBINED")
#         print("="*80 + "\n")
        
#         for i, article in enumerate(top_10_articles, 1):
#             importance_emoji = "🔥" if article.get('importance') == 'high' else "📌"
#             category_emoji = {
#                 'crime': '🚨',
#                 'politics': '🏛️',
#                 'general': '📰'
#             }.get(article.get('category', 'general'), '📰')
            
#             print(f"{i}. {importance_emoji} {category_emoji} [{article['source']}]")
#             print(f"\n   📋 शीर्षक: {article['title']}")
#             print(f"\n   📝 विस्तृत सारांश:")
#             print(f"   {article.get('detailed_summary', 'N/A')}")
            
#             if article.get('key_points'):
#                 print(f"\n   🔑 मुख्य मुद्दे:")
#                 for point in article['key_points']:
#                     print(f"      • {point}")
            
#             print(f"\n   🔗 {article['link']}")
#             print(f"   ⚡ महत्त्व: {article.get('importance', 'N/A').upper()}")
#             print("\n" + "-"*80 + "\n")
    
#     print("✅ Smart scraping complete! Top 10 news from all sites extracted.\n")


# if __name__ == "__main__":
#     asyncio.run(main())
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

# Initialize Perplexity client

perplexity_client = OpenAI(
    api_key=os.environ.get("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)


# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
GOOGLE_SHEET_NAME = "Instagram Scripts"
GOOGLE_WORKSHEET_NAME = "Scripts"


# Track token usage (CORRECTED: $1 per 1M tokens)
total_tokens_used = 0
total_cost = 0.0


def setup_google_sheets():
    """
    Initialize Google Sheets connection
    """
    try:
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load credentials
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE, 
            scopes=scope
        )
        
        # Authorize and connect
        client = gspread.authorize(creds)
        
        # Open or create spreadsheet
        try:
            sheet = client.open(GOOGLE_SHEET_NAME)
            print(f"✅ Connected to existing sheet: '{GOOGLE_SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(GOOGLE_SHEET_NAME)
            print(f"✅ Created new sheet: '{GOOGLE_SHEET_NAME}'")
        
        # Open or create worksheet
        try:
            worksheet = sheet.worksheet(GOOGLE_WORKSHEET_NAME)
            print(f"✅ Using worksheet: '{GOOGLE_WORKSHEET_NAME}'")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(
                title=GOOGLE_WORKSHEET_NAME,
                rows=1000,
                cols=10
            )
            # Add headers (only 4 columns now)
            worksheet.update('A1:D1', [[
                'Timestamp',
                'Title',
                'Script',
                'Source Link'
            ]])
            
            # Format headers (bold, colored background, white text)
            worksheet.format('A1:D1', {
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}  # White text
                },
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},  # Blue background
                'horizontalAlignment': 'CENTER'
            })
            
            # Set column widths
            worksheet.set_column_width('A', 180)  # Timestamp
            worksheet.set_column_width('B', 400)  # Title
            worksheet.set_column_width('C', 600)  # Script (wide)
            worksheet.set_column_width('D', 400)  # Source Link
            
            print(f"✅ Created new worksheet with headers: '{GOOGLE_WORKSHEET_NAME}'")
        
        return worksheet
        
    except FileNotFoundError:
        print(f"❌ Error: '{GOOGLE_SHEETS_CREDENTIALS_FILE}' not found!")
        print("💡 Download credentials from Google Cloud Console")
        return None
    except Exception as e:
        print(f"❌ Google Sheets setup error: {e}")
        return None


def save_to_google_sheets(worksheet, script, source_link, news_title):
    """
    Append script data to Google Sheets with proper formatting (no overwriting)
    Only saves: Timestamp, Title, Script, Source Link
    """
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # ✅ FIX: Ensure all values are proper strings (not lists)
        # Convert script to plain string if it's in any other format
        if isinstance(script, list):
            script = '\n'.join(str(item) for item in script)
        else:
            script = str(script).strip()
        
        # Clean up any remaining brackets from the script
        script = script.replace('[', '').replace(']', '')
        
        # Ensure other fields are also strings
        news_title = str(news_title).strip()
        source_link = str(source_link).strip()
        
        # Prepare row data (only 4 columns) - all as strings
        row_data = [
            timestamp,
            news_title,
            script,
            source_link
        ]
        
        # Get next row number
        next_row = len(worksheet.get_all_values()) + 1
        
        # Append to the sheet (after last row) with RAW string values
        worksheet.append_row(row_data, value_input_option='RAW')  # Changed from USER_ENTERED to RAW
        
        # Format the newly added row (BLACK text, white background, wrap text)
        row_range = f'A{next_row}:D{next_row}'
        worksheet.format(row_range, {
            'textFormat': {
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},  # BLACK text
                'fontSize': 10
            },
            'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},  # White background
            'wrapStrategy': 'WRAP',  # Wrap text in cells
            'verticalAlignment': 'TOP'
        })
        
        # Format Script column (C) specifically - wrap and left align
        worksheet.format(f'C{next_row}', {
            'textFormat': {
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},  # BLACK text
                'fontSize': 10
            },
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP',
            'horizontalAlignment': 'LEFT'
        })
        
        # Format Title column (B) - left align
        worksheet.format(f'B{next_row}', {
            'textFormat': {
                'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},  # BLACK text
                'fontSize': 10
            },
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP',
            'horizontalAlignment': 'LEFT'
        })
        
        # Format link column (D) - make it clickable blue
        worksheet.format(f'D{next_row}', {
            'textFormat': {
                'foregroundColor': {'red': 0.06, 'green': 0.27, 'blue': 0.8},  # Blue text
                'fontSize': 10,
                'underline': True
            },
            'wrapStrategy': 'WRAP',
            'verticalAlignment': 'TOP'
        })
        
        print(f"✅ Script saved to Google Sheets!")
        print(f"   Row #{next_row} added with timestamp: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving to Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return False


async def scrape_marathi_news_final():
    """
    Scraper that collects articles from all three sites
    """
    
    news_sites = [
        {
            "name": "TV9 Marathi",
            "url": "https://www.tv9marathi.com/latest-news",
            "article_selector": "article, div.story-card, div.news-item",
            "link_pattern": "tv9marathi.com"
        },
        {
            "name": "ABP Majha",
            "url": "https://marathi.abplive.com/news",
            "article_selector": "article, div.story-box, div.news-card",
            "link_pattern": "abplive.com"
        },
        {
            "name": "Lokmat",
            "url": "https://www.lokmat.com/latestnews/",
            "article_selector": "article, div.story-card, div.card-body",
            "link_pattern": "lokmat.com"
        }
    ]
    
    all_news = []
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        
        for site in news_sites:
            print(f"\n🔍 Scraping {site['name']}...")
            
            try:
                # Step 1: Fetch homepage with JavaScript rendering
                config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    wait_for="body",
                    word_count_threshold=10,
                    page_timeout=30000,
                    js_code="""
                    // Wait for content to load
                    await new Promise(r => setTimeout(r, 2000));
                    """
                )
                
                result = await crawler.arun(site['url'], config=config)
                
                if result.success:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    raw_articles = []
                    
                    # Strategy: Find all links with Marathi text
                    all_links = soup.find_all('a', href=True)
                    
                    for link_tag in all_links:
                        href = link_tag.get('href', '')
                        title = link_tag.get_text(strip=True)
                        
                        # Filter valid news links
                        if (len(title) > 15 and len(title) < 300 and
                            site['link_pattern'] in href and
                            not any(x in href for x in [
                                'javascript:', 'mailto:', '#', 
                                '/category/', '/tag/', '/author/',
                                'facebook.com', 'twitter.com', 'instagram.com',
                                'youtube.com', 'whatsapp.com', '/myaccount/',
                                '/install_app', '/advertisement', '/epaper',
                                'web-stories', 'photo-gallery', '/videos/',
                                '/sakhi/', '/astro/', '/bhakti/', '/games/',
                                '/jokes/', '/terms-and-conditions', '/utility-news',
                                '/spiritual-adhyatmik', '/rashi-bhavishya', 
                                '/topic/', '/elections/', '/career/'
                            ])):
                            
                            # Make absolute URL
                            if href.startswith('/'):
                                base_url = site['url'].split('/')[0] + '//' + site['url'].split('/')[2]
                                href = base_url + href
                            
                            if href.startswith('http'):
                                raw_articles.append({
                                    'title': title,
                                    'link': href
                                })
                    
                    # Remove duplicates by link
                    seen_links = set()
                    unique_articles = []
                    for article in raw_articles:
                        if article['link'] not in seen_links:
                            unique_articles.append(article)
                            seen_links.add(article['link'])
                    
                    print(f"📋 Found {len(unique_articles)} unique articles from {site['name']}")
                    
                    if len(unique_articles) > 0:
                        # CHANGED: Get top 10-15 articles per site (not 20)
                        print(f"📄 Fetching detailed content from top {min(12, len(unique_articles))} articles...")
                        
                        articles_with_content = []
                        for article in unique_articles[:12]:  # Top 12 per site
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
                                    articles_with_content.append({
                                        'title': article['title'],
                                        'link': article['link'],
                                        'content': article_result.markdown[:2500]
                                    })
                                    print(f"   ✓ {article['title'][:60]}...")
                                    
                            except Exception as e:
                                continue
                        
                        print(f"✅ Fetched content for {len(articles_with_content)} articles")
                        
                        # Step 3: AI analysis
                        if articles_with_content:
                            filtered_news = await smart_analyze_with_detailed_summary(
                                articles_with_content, 
                                site['name']
                            )
                            all_news.extend(filtered_news)
                            print(f"✅ Extracted {len(filtered_news)} important articles with detailed summaries")
                    else:
                        print(f"⚠️ No articles found from {site['name']}")
                
                else:
                    print(f"❌ Failed to fetch {site['name']}: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ Error scraping {site['name']}: {e}")
                import traceback
                traceback.print_exc()
    
    return all_news


async def smart_analyze_with_detailed_summary(articles, source_name):
    """
    AI analysis with CORRECTED token tracking ($1 per 1M tokens)
    """
    global total_tokens_used, total_cost
    
    print(f"\n🧠 Using AI for detailed analysis of {source_name} articles...")
    
    all_filtered = []
    
    # Process in batches of 5
    for i in range(0, len(articles), 5):
        batch = articles[i:i+5]
        
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
तुम्ही एक तज्ञ मराठी बातम्या विश्लेषक आहात. खालील बातम्यांचे विश्लेषण करा.


**फक्त हे प्रकार निवडा:**
1. गुन्हेगारी बातम्या (Crime) - हत्या, दरोडा, अपघात, अटक, लाच
2. राजकीय बातम्या (Political) - निवडणुका, सरकार, महापालिका, राजकीय घडामोडी
3. महत्त्वाच्या सामान्य बातम्या (Important General) - शासकीय निर्णय, सामाजिक मुद्दे


**टाळावे:** मनोरंजन gossip, ज्योतिष, फॅशन, lifestyle, खेळाची सामान्य बातमी, job posts, धार्मिक कथा, Bigg Boss, बॉलीवूड gossip


**JSON format (फक्त array परत करा, इतर काही नाही):**
[
  {{
    "title": "मूळ शीर्षक",
    "category": "crime/politics/general",
    "detailed_summary": "संपूर्ण विस्तृत सारांश 150-250 शब्दांत मराठीत. काय घडलं? कुठे? कधी? कोण आहेत? कोणती कारवाई? काय परिणाम? इतर तपशील समाविष्ट करा",
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
                        "content": "You are an expert Marathi news analyst. Return ONLY valid JSON array. No markdown, no explanation, no extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Track tokens (CORRECTED: $1 per 1M tokens)
            if hasattr(response, 'usage'):
                batch_tokens = response.usage.total_tokens
                total_tokens_used += batch_tokens
                
                # CORRECT pricing: $1 per 1M tokens
                batch_cost = (batch_tokens / 1_000_000) * 1.0
                total_cost += batch_cost
                
                print(f"   📊 Batch tokens: {batch_tokens:,} | Cost: ${batch_cost:.4f}")
            
            content = response.choices[0].message.content
            
            # Extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                batch_articles = json.loads(json_match.group())
                all_filtered.extend(batch_articles)
                print(f"   ✅ Extracted {len(batch_articles)} articles from this batch")
            else:
                print(f"   ⚠️ No valid JSON in AI response")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"   ❌ AI analysis error: {e}")
    
    # Add source and timestamp
    for article in all_filtered:
        article['source'] = source_name
        article['scraped_at'] = datetime.now().isoformat()
    
    return all_filtered


def create_reel_script(news_articles):
    """
    Generate ONE Instagram Reel script from news articles (takes list, returns one script)
    Returns: (script, source_link, news_title)
    """
    global total_tokens_used, total_cost
    
    # Prepare news summary for AI
    news_context = ""
    for idx, article in enumerate(news_articles[:5], 1):  # Use top 5 for context
        news_context += f"""
बातमी #{idx}:
शीर्षक: {article['title']}
प्रकार: {article['category']}
सारांश: {article['detailed_summary']}
महत्त्व: {article['importance']}
लिंक: {article['link']}
---
"""
    
    # System prompt with DIVERSE hook examples
    system_prompt = """
तुम्ही "जबरी खबरी" Instagram Reels चे एक्सपर्ट स्क्रिप्ट रायटर आहात.


**CRITICAL: HOOK VARIETY (पहिल्या 2 ओळी) - MUST USE DIFFERENT STYLES:**


**Hook Style 1: Shock Statement (तथ्यात्मक धक्का)**
- "एका अपघाताने संपूर्ण राज्य हादरलं."
- "तीन वर्षाच्या मुलीसमोर आईने संपवलं आयुष्य."
- "आता या क्षणाची सगळ्यात मोठी बातमी येतीये."


**Hook Style 2: Direct Question (थेट प्रश्न)**
- "तुम्हाला माहिती आहे का, विमानातला ब्लॅक बॉक्स ब्लॅक नसतो?"
- "कधी विचार केलाय का, देश चालवणारे लोक कसे नियतीच्या झटक्यात हरपतात?"
- "याबद्दल ऐकलंय का तुम्ही?"


**Hook Style 3: Breaking News (ब्रेकिंग अंदाज)**
- "नुकतीच एक धक्कादायक माहिती समोर आली आहे."
- "काल रात्री घडलेली ही घटना आज चर्चेत आहे."
- "सोशल मीडियावर व्हायरल होतेय हे प्रकरण."


**Hook Style 4: Name Drop (नावाने सुरुवात)**
- "बाबासाहेबांचं नाव टाळलेलं खपवून घेणार नाही."
- "अजित दादा म्हणजे फक्त राजकारण नाही."
- "[व्यक्ती/ठिकाण नाव] आज चर्चेत का आहे?"


**Hook Style 5: Contrast/Twist (विरोधाभास)**
- "दिसतं काहीतरी, पण वास्तव काहीतरी वेगळंच."
- "सगळ्यांना वाटतं असं, पण खरं काय आहे?"
- "साडी म्हणजे फक्त फॅशन नाही, याआड एक मोठा संदेश आहे."


**⚠️ WARNING: प्रत्येक script वेगळ्या hook style ने सुरू करा. SAME hook पुन्हा वापरू नका!**


---


**स्टोरी स्ट्रक्चर (40-60 seconds):**
- पहिले 2 ओळी: शॉकिंग/प्रश्नात्मक/ब्रेकिंग hook (वरील 5 styles पैकी एक)
- 3-10 ओळी: मुख्य घटना (कोण/काय/कुठे/कधी/कशी) - तपशीलवार
- 11-14 ओळी: ट्विस्ट/प्रश्न/विश्लेषण - "आता प्रश्न असा..." किंवा "पण एक गोष्ट नक्की..."
- शेवटच्या 2-3 ओळी: Call to Action


**भाषा स्टाईल:**
- संभाषणात्मक मराठी (formal news भाषा नाही!)
- भावनिक शब्द: "हादरलं", "धक्कादायक", "सुन्न करणारी", "चटका लावून जाणारा"
- प्रश्नात्मक वळण: "असा प्रश्न उपस्थित होतोय की..."
- थेट संवाद: "तुमचं काय मत आहे?"


**TONE BY CATEGORY:**
- CRIME: शॉकिंग + प्रश्नांकित ("कसं शक्य झालं? कोणी तपासलं नाही का?")
- POLITICS: नाट्यमय + विश्लेषणात्मक ("राजकारणातली ही चाल काय आहे?")
- GENERAL: माहितीपूर्ण + रंजक ("ही गोष्ट तुम्हाला माहिती होती का?")


**SIGNATURE ENDING (शेवटच्या 2-3 ओळी - यापैकी एक वापरा):**
- "तुमचं काय मत आहे? कमेंट करून सांगा आणि अशाच अपडेटसाठी फॉलो करा जबरी खबरी."
- "ही घटना तुम्हाला कशी वाटली? आम्हाला कमेंट करून नक्की सांगा आणि फॉलो करा जबरी खबरी."
- "या प्रकरणात तुमचा काय अभिप्राय? कमेंटमध्ये नक्की सांगा आणि अशाच जबरी अपडेटसाठी फॉलो करा."


**FORBIDDEN:**
❌ प्रत्येक reel "कधी विचार केलाय का" ने सुरू करणे
❌ समान hook pattern पुन्हा वापरणे
❌ बुलेट पॉइंट्स किंवा lists
❌ फॉर्मल न्यूज भाषा
❌ 15+ शब्दांची लांब वाक्ये


**OUTPUT FORMAT:**
फक्त स्क्रिप्ट परत करा. 15-18 ओळी. प्रत्येक reel साठी DIFFERENT hook style निवडा.


**IMPORTANT:** script शेवटी तुम्ही कोणती बातमी वापरली ते सांगा:
Format: [SCRIPT]\n\n---ARTICLE_NUMBER: X---
"""
    
    # User prompt
    user_prompt = f"""
खालील आजच्या TOP बातम्यांपैकी सर्वात ENGAGING आणि VIRAL होण्याची क्षमता असलेली बातमी निवडून त्यावर एक Instagram Reel script तयार करा.


**निवड करताना:**
1. CRIME बातम्या प्राधान्य (सर्वाधिक viral)
2. SHOCKING किंवा CONTROVERSIAL बातम्या पुढे
3. EMOTIONAL CONNECTION असलेल्या गोष्टी


**आजच्या बातम्या:**
{news_context}


**तुमचं काम:**
1. वरील बातम्यांपैकी सर्वात STRONG बातमी निवडा
2. **5 HOOK STYLES पैकी बातमीला सर्वात योग्य hook निवडा** (कधी विचार केलाय का - हा फक्त एक option आहे!)
3. Jabari Khabari च्या EXACT स्टाईलमध्ये 15-18 ओळींची script लिहा
4. संभाषणात्मक, नाट्यमय, प्रश्नात्मक भाषा वापरा
5. शेवटी article number द्या


**CRITICAL: Hook MUST be VARIED. बातमीच्या स्वरूपानुसार योग्य hook style निवडा!**


OUTPUT FORMAT:
[तुमची script]


---ARTICLE_NUMBER: X---
"""
    
    # Call Perplexity API
    try:
        response = perplexity_client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.8,  # Increased for more creativity/variety
            max_tokens=1500
        )
        
        # Track tokens
        if hasattr(response, 'usage'):
            script_tokens = response.usage.total_tokens
            total_tokens_used += script_tokens
            script_cost = (script_tokens / 1_000_000) * 1.0
            total_cost += script_cost
        
        full_response = response.choices[0].message.content.strip()
        
        # Extract script and article number
        if "---ARTICLE_NUMBER:" in full_response:
            parts = full_response.split("---ARTICLE_NUMBER:")
            script = parts[0].strip()
            article_num_str = parts[1].strip().replace("---", "").strip()
            try:
                article_num = int(article_num_str) - 1  # Convert to 0-indexed
            except:
                article_num = 0  # Default to first article
        else:
            script = full_response
            article_num = 0  # Default to first article
        
        # Clean up the script
        script = script.replace('```', '').strip()
        script = script.replace('---ARTICLE_NUMBER:', '').strip()
        
        # Get source article details
        if article_num < len(news_articles):
            source_article = news_articles[article_num]
            source_link = source_article.get('link', 'N/A')
            news_title = source_article.get('title', 'N/A')
        else:
            source_article = news_articles
            source_link = source_article.get('link', 'N/A')
            news_title = source_article.get('title', 'N/A')
        
        return script, source_link, news_title
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        return None, None, None


async def main():
    global total_tokens_used, total_cost
    
    print("🚀 Starting Smart Marathi News Scraper + Script Generator")
    print("📍 Focus: Criminal, Political & Important General News")
    print("📝 Feature: Detailed summaries + Instagram Scripts")
    print("💰 Token tracking enabled")
    print("📊 Output: Direct to Google Sheets (No local files)\n")
    
    start_time = datetime.now()
    
    # ===== PART 1: SCRAPING (NO CHANGES) =====
    all_articles = await scrape_marathi_news_final()
    
    # Remove duplicates by title
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
        title_lower = article['title'].lower()
        if title_lower not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(title_lower)
    
    # Sort ALL articles by importance FIRST
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    unique_articles.sort(key=lambda x: priority_order.get(x.get('importance', 'medium'), 2))
    
    # ❌ REMOVED: JSON file saving
    # Get TOP 10
    top_10_articles = unique_articles[:10]
    
    end_scrape = datetime.now()
    scrape_duration = (end_scrape - start_time).total_seconds()
    
    # Scraping summary
    print("\n" + "="*80)
    print("📊 SCRAPING SUMMARY")
    print("="*80)
    print(f"   Total articles scraped: {len(unique_articles)}")
    print(f"   High importance: {len([a for a in unique_articles if a.get('importance') == 'high'])}")
    print(f"   Crime news: {len([a for a in unique_articles if a.get('category') == 'crime'])}")
    print(f"   Political news: {len([a for a in unique_articles if a.get('category') == 'politics'])}")
    print(f"   General news: {len([a for a in unique_articles if a.get('category') == 'general'])}")
    print(f"\n   By source:")
    for source in ['TV9 Marathi', 'ABP Majha', 'Lokmat']:
        count = len([a for a in unique_articles if a['source'] == source])
        count_top10 = len([a for a in top_10_articles if a['source'] == source])
        print(f"      • {source}: {count} total | {count_top10} in TOP 10")
    print(f"\n⏱️  Scraping time: {scrape_duration:.2f} seconds")
    print("="*80 + "\n")
    
    # ===== PART 2: SCRIPT GENERATION (PASS DATA DIRECTLY) =====
    print("="*80)
    print("🎬 GENERATING INSTAGRAM SCRIPTS")
    print("="*80 + "\n")
    
    # Setup Google Sheets
    worksheet = setup_google_sheets()
    
    if worksheet and len(top_10_articles) > 0:
        print(f"\n🎯 Generating script from TOP 10 articles...\n")
        
        # Generate ONE script from top 10
        script, source_link, news_title = create_reel_script(top_10_articles)
        
        if script:
            print("\n" + "="*70)
            print("📝 GENERATED SCRIPT:")
            print("="*70)
            print(script)
            print("\n" + "="*70)
            print(f"📰 Title: {news_title}")
            print(f"🔗 Source: {source_link}")
            print("="*70 + "\n")
            
            # Save to Google Sheets
            success = save_to_google_sheets(worksheet, script, source_link, news_title)
            
            if success:
                print(f"📈 View your sheet: https://docs.google.com/spreadsheets/d/{worksheet.spreadsheet.id}")
        else:
            print("❌ Failed to generate script")
    else:
        print("⚠️ No articles or Google Sheets unavailable")
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Final summary
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)
    print(f"   Total articles scraped: {len(unique_articles)}")
    print(f"   Scripts generated: 1")
    print(f"   Saved to: {GOOGLE_SHEET_NAME}")
    print(f"\n   ⏱️ Total time: {total_duration:.2f} seconds")
    print(f"   🔢 Total tokens: {total_tokens_used:,}")
    print(f"   💰 Total cost: ${total_cost:.4f}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())