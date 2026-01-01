#!/usr/bin/env python3
"""
Reddit Overnight Scraper - CONTINUATION
Runs ONLY the remaining searches (5-12) to avoid duplicates
Use this after the first run got rate-limited
"""

import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

class RedditScraperContinuation:
    """Continue scraping from where we left off"""
    
    def __init__(self, output_dir='optimus_data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.all_data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def load_existing_data(self):
        """Load data from previous run"""
        existing_file = self.output_dir / 'optimus_reddit_OVERNIGHT_20251231_235901.csv'
        
        if existing_file.exists():
            print(f"📂 Loading existing data from: {existing_file.name}")
            df = pd.read_csv(existing_file)
            print(f"✓ Loaded {len(df)} existing items")
            
            # Convert to list of dicts
            self.all_data = df.to_dict('records')
            return True
        else:
            print("⚠️ No existing data found. Starting fresh.")
            return False
    
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
    
    def run_remaining_searches(self, search_configs, wait_minutes=3):
        """Run remaining searches with longer wait times"""
        total_configs = len(search_configs)
        
        print(f"\n{'='*60}")
        print(f"CONTINUATION - REMAINING SEARCHES")
        print(f"{'='*60}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Searches to run: {total_configs}")
        print(f"Wait between searches: {wait_minutes} minutes")
        print(f"Estimated time: {total_configs * wait_minutes} minutes")
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
            
            # LONGER delay between searches
            if idx < total_configs:
                wait_seconds = wait_minutes * 60
                print(f"\n⏸️ Waiting {wait_minutes} minutes before next search...")
                print(f"   (This avoids rate limiting)")
                time.sleep(wait_seconds)
        
        print(f"\n{'='*60}")
        print(f"ALL REMAINING SEARCHES COMPLETE")
        print(f"{'='*60}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total items collected: {len(self.all_data)}")
    
    def save_progress(self):
        """Save current progress"""
        if not self.all_data:
            return
        
        df = pd.DataFrame(self.all_data)
        progress_file = self.output_dir / 'continuation_progress.csv'
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
        filepath = self.output_dir / f'optimus_reddit_COMPLETE_{timestamp}.csv'
        df.to_csv(filepath, index=False)
        
        print(f"\n{'='*60}")
        print(f"✓ FINAL DATA SAVED")
        print(f"{'='*60}")
        print(f"File: {filepath}")
        print(f"Total items: {len(df)}")
        
        # Save sample
        sample_path = self.output_dir / 'optimus_reddit_COMPLETE_sample.csv'
        df.head(100).to_csv(sample_path, index=False)
        print(f"Sample: {sample_path}")
        
        # Clean up progress file
        progress_file = self.output_dir / 'continuation_progress.csv'
        if progress_file.exists():
            progress_file.unlink()
        
        return df


def main():
    """Run remaining searches only"""
    
    # REMAINING SEARCHES (5-12)
    remaining_searches = [
        # Search 5 - r/robotics
        {'subreddit': 'robotics', 'query': 'optimus robot', 'limit': 50},
        
        # Search 6-7 - r/technology
        {'subreddit': 'technology', 'query': 'tesla optimus', 'limit': 100},
        {'subreddit': 'technology', 'query': 'optimus robot', 'limit': 50},
        
        # Search 8-9 - r/Futurology
        {'subreddit': 'Futurology', 'query': 'tesla optimus', 'limit': 100},
        {'subreddit': 'Futurology', 'query': 'optimus humanoid', 'limit': 50},
        
        # Search 10-11 - r/artificial
        {'subreddit': 'artificial', 'query': 'tesla optimus', 'limit': 50},
        {'subreddit': 'artificial', 'query': 'optimus robot', 'limit': 50},
        
        # Search 12 - r/RealTesla
        {'subreddit': 'RealTesla', 'query': 'optimus', 'limit': 100},
    ]
    
    total_posts = sum(c['limit'] for c in remaining_searches)
    
    print("\n" + "="*60)
    print("CONTINUATION SCRAPER - REMAINING SEARCHES")
    print("="*60)
    print("\nThis will CONTINUE from where you left off.")
    print("It will load your existing 1,606 items and add more.\n")
    print(f"Remaining searches: {len(remaining_searches)}")
    print(f"Target posts: {total_posts}")
    
    print(f"\nSearches planned:")
    for idx, config in enumerate(remaining_searches, 1):
        print(f"  {idx}. r/{config['subreddit']} - '{config['query']}' ({config['limit']} posts)")
    
    wait_minutes = 3
    print(f"\n⏱️ Wait between searches: {wait_minutes} minutes")
    print(f"💾 Total estimated time: {len(remaining_searches) * wait_minutes} minutes (~{len(remaining_searches) * wait_minutes / 60:.1f} hours)")
    print(f"🛑 Press Ctrl+C to stop (progress will be saved)")
    
    print("\n" + "="*60)
    response = input("\nReady to continue collection? (y/N): ").strip().lower()
    
    if response != 'y':
        print("\nCancelled.")
        return
    
    print("\n🚀 Starting continuation...")
    
    try:
        scraper = RedditScraperContinuation()
        
        # Load existing data
        scraper.load_existing_data()
        
        # Run remaining searches
        scraper.run_remaining_searches(remaining_searches, wait_minutes=wait_minutes)
        
        # Finalize
        df = scraper.finalize_data()
        
        if df is not None and not df.empty:
            print("\n✅ COLLECTION COMPLETE!")
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
        print("✓ Progress saved!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Attempting to save progress...")
        try:
            scraper.finalize_data()
        except:
            pass


if __name__ == "__main__":
    main()
