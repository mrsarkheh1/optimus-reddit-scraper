#!/usr/bin/env python3
"""
Reddit Overnight Scraper - AUTOMATED
Runs multiple searches with different keywords automatically
Perfect for running overnight to collect maximum data
"""

import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

class OvernightRedditScraper:
    """Automated scraper for running multiple searches overnight"""
    
    def __init__(self, output_dir='optimus_data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.all_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_subreddit(self, subreddit, query, limit=100):
        """Search a subreddit using JSON API"""
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Searching r/{subreddit} for '{query}'")
        print(f"Target: {limit} posts")
        print(f"{'='*60}\n")
        
        url = f"https://old.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'comments',
            'limit': min(limit, 100)
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            posts = data['data']['children']
            print(f"✓ Found {len(posts)} posts")
            
            if len(posts) == 0:
                print("⚠️ No posts found for this query")
                return 0
            
            items_collected = 0
            
            for idx, post in enumerate(posts, 1):
                post_data = post['data']
                
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                author = post_data.get('author', 'unknown')
                score = post_data.get('score', 0)
                num_comments = post_data.get('num_comments', 0)
                permalink = post_data.get('permalink', '')
                post_url = f"https://old.reddit.com{permalink}"
                
                # Store post
                self.all_data.append({
                    'type': 'post',
                    'title': title,
                    'text': selftext,
                    'combined_text': f"{title} {selftext}",
                    'author': author,
                    'score': score,
                    'num_comments': num_comments,
                    'url': post_url,
                    'search_query': query,
                    'subreddit': subreddit,
                    'date_scraped': datetime.now().isoformat()
                })
                items_collected += 1
                
                # Get comments
                if num_comments > 0:
                    comment_count = self.get_comments(post_url, title, query, subreddit)
                    items_collected += comment_count
                
                # Progress indicator
                if idx % 10 == 0:
                    print(f"  [{idx}/{len(posts)}] Processed {items_collected} total items...")
                
                time.sleep(2)  # Be respectful
            
            print(f"✓ Collected {items_collected} items from this search")
            return items_collected
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    def get_comments(self, post_url, post_title, search_query, subreddit):
        """Get comments from a post"""
        try:
            json_url = post_url + '.json'
            response = requests.get(json_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2:
                return 0
            
            comments_listing = data[1]['data']['children']
            comment_count = 0
            
            for comment in comments_listing[:20]:
                if comment['kind'] != 't1':
                    continue
                
                comment_data = comment['data']
                body = comment_data.get('body', '')
                
                if body in ['[deleted]', '[removed]', ''] or len(body) < 30:
                    continue
                
                author = comment_data.get('author', 'unknown')
                score = comment_data.get('score', 0)
                
                self.all_data.append({
                    'type': 'comment',
                    'title': f"Comment on: {post_title[:50]}...",
                    'text': body,
                    'combined_text': body,
                    'author': author,
                    'score': score,
                    'num_comments': 0,
                    'url': post_url,
                    'search_query': search_query,
                    'subreddit': subreddit,
                    'date_scraped': datetime.now().isoformat()
                })
                comment_count += 1
            
            return comment_count
        
        except:
            return 0
    
    def run_automated_searches(self, search_configs):
        """Run multiple searches automatically"""
        total_configs = len(search_configs)
        
        print(f"\n{'='*60}")
        print(f"OVERNIGHT AUTOMATION STARTED")
        print(f"{'='*60}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total searches planned: {total_configs}")
        print(f"Wait between searches: 3 minutes")
        print(f"Estimated time: {total_configs * 3} minutes (~{total_configs * 3 / 60:.1f} hours)")
        print(f"{'='*60}\n")
        
        for idx, config in enumerate(search_configs, 1):
            print(f"\n{'#'*60}")
            print(f"SEARCH {idx}/{total_configs}")
            print(f"{'#'*60}")
            
            items = self.search_subreddit(
                subreddit=config['subreddit'],
                query=config['query'],
                limit=config['limit']
            )
            
            print(f"\n→ Running total: {len(self.all_data)} items collected")
            
            # Save progress after each search
            self.save_progress()
            
            # Wait 3 minutes between searches to avoid rate limiting
            if idx < total_configs:
                print(f"\n⏸️ Waiting 3 minutes before next search...")
                print(f"   (Avoids Reddit rate limiting)")
                time.sleep(180)  # 3 minutes = 180 seconds
        
        print(f"\n{'='*60}")
        print(f"ALL SEARCHES COMPLETE")
        print(f"{'='*60}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total items collected: {len(self.all_data)}")
    
    def save_progress(self):
        """Save current progress"""
        if not self.all_data:
            return
        
        df = pd.DataFrame(self.all_data)
        progress_file = self.output_dir / 'overnight_progress.csv'
        df.to_csv(progress_file, index=False)
    
    def finalize_data(self):
        """Clean and save final dataset"""
        if not self.all_data:
            print("\n⚠️ No data collected!")
            return None
        
        df = pd.DataFrame(self.all_data)
        
        print(f"\n{'='*60}")
        print("FINAL DATA PROCESSING")
        print(f"{'='*60}")
        print(f"Raw items: {len(df)}")
        
        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates(subset=['combined_text'], keep='first')
        print(f"  → Removed {before - len(df)} duplicates")
        
        # Remove short items
        before = len(df)
        df = df[df['combined_text'].str.len() >= 30]
        print(f"  → Removed {before - len(df)} items under 30 chars")
        
        # Add analysis columns
        df['text_length'] = df['combined_text'].str.len()
        keywords = ['like', 'seems', 'feels', 'acts', 'is a', 'become', 'as if', 'reminds']
        df['has_metaphor'] = df['combined_text'].str.contains('|'.join(keywords), case=False, na=False)
        
        print(f"\n✓ Final dataset: {len(df)} items")
        print(f"  Posts: {len(df[df['type'] == 'post'])}")
        print(f"  Comments: {len(df[df['type'] == 'comment'])}")
        print(f"  Unique subreddits: {df['subreddit'].nunique()}")
        print(f"  Unique search queries: {df['search_query'].nunique()}")
        
        # Metaphor analysis
        metaphor_count = df['has_metaphor'].sum()
        print(f"\n🎯 Metaphor Signals: {metaphor_count} ({100*metaphor_count/len(df):.1f}%)")
        
        # Save final file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.output_dir / f'optimus_reddit_OVERNIGHT_{timestamp}.csv'
        
        df.to_csv(filepath, index=False)
        
        print(f"\n{'='*60}")
        print(f"✓ FINAL DATA SAVED")
        print(f"{'='*60}")
        print(f"File: {filepath}")
        print(f"Total items: {len(df)}")
        
        # Save sample
        sample_path = self.output_dir / 'optimus_reddit_OVERNIGHT_sample.csv'
        df.head(100).to_csv(sample_path, index=False)
        print(f"Sample: {sample_path}")
        
        # Clean up progress file
        progress_file = self.output_dir / 'overnight_progress.csv'
        if progress_file.exists():
            progress_file.unlink()
        
        return df


def main():
    """Main execution with predefined search configurations"""
    
    # CONFIGURATION: Customize your searches here
    search_configs = [
        # r/teslamotors - primary source
        {'subreddit': 'teslamotors', 'query': 'optimus', 'limit': 100},
        {'subreddit': 'teslamotors', 'query': 'tesla robot', 'limit': 50},
        {'subreddit': 'teslamotors', 'query': 'humanoid robot', 'limit': 50},
        
        # r/robotics - technical perspective
        {'subreddit': 'robotics', 'query': 'tesla optimus', 'limit': 100},
        {'subreddit': 'robotics', 'query': 'optimus robot', 'limit': 50},
        
        # r/technology - general tech audience
        {'subreddit': 'technology', 'query': 'tesla optimus', 'limit': 100},
        {'subreddit': 'technology', 'query': 'optimus robot', 'limit': 50},
        
        # r/Futurology - speculative discourse
        {'subreddit': 'Futurology', 'query': 'tesla optimus', 'limit': 100},
        {'subreddit': 'Futurology', 'query': 'optimus humanoid', 'limit': 50},
        
        # r/artificial - AI perspective
        {'subreddit': 'artificial', 'query': 'tesla optimus', 'limit': 50},
        {'subreddit': 'artificial', 'query': 'optimus robot', 'limit': 50},
        
        # r/RealTesla - skeptical/critical perspective
        {'subreddit': 'RealTesla', 'query': 'optimus', 'limit': 100},
    ]
    
    # Calculate totals
    total_posts = sum(c['limit'] for c in search_configs)
    estimated_items = total_posts * 12  # Assuming ~12 items per post (post + comments)
    
    print("\n" + "="*60)
    print("OVERNIGHT REDDIT SCRAPER - AUTOMATED")
    print("="*60)
    print("\nThis will run AUTOMATICALLY with these searches:")
    print(f"\nTotal searches: {len(search_configs)}")
    print(f"Total posts target: {total_posts}")
    print(f"Estimated items: ~{estimated_items}")
    print(f"\nSearches planned:")
    for idx, config in enumerate(search_configs, 1):
        print(f"  {idx}. r/{config['subreddit']} - '{config['query']}' ({config['limit']} posts)")
    
    print(f"\n⏱️ Estimated time: {len(search_configs) * 3} minutes (~{len(search_configs) * 3 / 60:.1f} hours)")
    print(f"💾 Progress saved after each search")
    print(f"🛑 Press Ctrl+C to stop (progress will be saved)")
    
    print("\n" + "="*60)
    response = input("\nReady to start overnight collection? (y/N): ").strip().lower()
    
    if response != 'y':
        print("\nCancelled. No data collected.")
        return
    
    print("\n🚀 Starting automated collection...")
    
    try:
        scraper = OvernightRedditScraper()
        scraper.run_automated_searches(search_configs)
        
        df = scraper.finalize_data()
        
        if df is not None and not df.empty:
            print("\n✅ OVERNIGHT COLLECTION COMPLETE!")
            print("\nNext steps:")
            print("1. Review the CSV file")
            print("2. Convert to JSONL for Gemini")
            print("3. Process through Vertex AI Batch API")
        else:
            print("\n⚠️ No data collected")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ INTERRUPTED BY USER")
        print("Saving progress...")
        scraper.finalize_data()
        print("✓ Progress saved! You can process what was collected.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Attempting to save progress...")
        try:
            scraper.finalize_data()
        except:
            pass


if __name__ == "__main__":
    main()
