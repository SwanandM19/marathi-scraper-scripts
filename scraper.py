import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import os

# Initialize Perplexity client with environment variable
perplexity_client = OpenAI(
    api_key=os.environ.get("PERPLEXITY_API_KEY"),  # Read from GitHub Secrets
    base_url="https://api.perplexity.ai"
)

# Track token usage (CORRECTED: $1 per 1M tokens)
total_tokens_used = 0
total_cost = 0.0

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
                        # Get top 12 articles per site
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


async def main():
    global total_tokens_used, total_cost
    
    print("🚀 Starting Smart Marathi News Scraper with DETAILED Summaries")
    print("📍 Focus: Criminal, Political & Important General News")
    print("📝 Feature: Detailed 150-250 word summaries")
    print("💰 Token tracking enabled (Correct pricing: $1/1M tokens)")
    print("🎯 Strategy: Get top 10 news from ALL THREE SITES COMBINED\n")
    
    start_time = datetime.now()
    
    # Scrape all sites
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
    
    # Save ALL articles to JSON (fixed filename)
    output_file = "latest_news.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    
    # Save TOP 10 to separate file (fixed filename)
    top_10_articles = unique_articles[:10]
    top_10_file = "top_10_latest.json"
    with open(top_10_file, 'w', encoding='utf-8') as f:
        json.dump(top_10_articles, f, ensure_ascii=False, indent=2)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Final summary
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
        print(f"      • {source}: {count} total articles | {count_top10} in TOP 10")
    print(f"\n💾 All articles saved to: {output_file}")
    print(f"🏆 TOP 10 articles saved to: {top_10_file}")
    print(f"\n⏱️  Total time: {duration:.2f} seconds")
    print(f"🔢 Total tokens used: {total_tokens_used:,}")
    print(f"💰 Estimated cost: ${total_cost:.4f} (@ $1.00 per 1M tokens)")
    if len(unique_articles) > 0:
        print(f"📈 Average tokens per article: {total_tokens_used // len(unique_articles):,}")
    print("="*80 + "\n")
    
    # Display TOP 10 from ALL sites combined
    if len(top_10_articles) > 0:
        print("🏆 TOP 10 IMPORTANT NEWS FROM ALL THREE SITES COMBINED")
        print("="*80 + "\n")
        
        for i, article in enumerate(top_10_articles, 1):
            importance_emoji = "🔥" if article.get('importance') == 'high' else "📌"
            category_emoji = {
                'crime': '🚨',
                'politics': '🏛️',
                'general': '📰'
            }.get(article.get('category', 'general'), '📰')
            
            print(f"{i}. {importance_emoji} {category_emoji} [{article['source']}]")
            print(f"\n   📋 शीर्षक: {article['title']}")
            print(f"\n   📝 विस्तृत सारांश:")
            print(f"   {article.get('detailed_summary', 'N/A')}")
            
            if article.get('key_points'):
                print(f"\n   🔑 मुख्य मुद्दे:")
                for point in article['key_points']:
                    print(f"      • {point}")
            
            print(f"\n   🔗 {article['link']}")
            print(f"   ⚡ महत्त्व: {article.get('importance', 'N/A').upper()}")
            print("\n" + "-"*80 + "\n")
    
    print("✅ Smart scraping complete! Top 10 news from all sites extracted.\n")


if __name__ == "__main__":
    asyncio.run(main())
