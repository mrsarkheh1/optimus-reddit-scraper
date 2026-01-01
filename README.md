# Tesla Optimus Reddit Scraper

Automated Reddit data collection tool for academic research on user-generated metaphors about Tesla's Optimus humanoid robot.

## Overview

This scraper collects Reddit discussions about Tesla Optimus across multiple subreddits to analyze how users metaphorically frame their relationship with AI/robotic devices. Part of research applying the Metaphor Hacking methodology to home AI and robotic companions.

## Features

- **Automated multi-search**: 12 searches across 6 subreddits
- **Rate limit protection**: 3-minute waits between searches
- **Progress saving**: Auto-saves after each search
- **Duplicate removal**: Automatic deduplication
- **Metaphor signal detection**: Flags potential metaphorical language
- **Multiple perspectives**: Collects from enthusiast, technical, critical communities

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/optimus-reddit-scraper.git
cd optimus-reddit-scraper

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python reddit_overnight_scraper_3min.py
```

Follow prompts to start collection.

### What It Collects

**12 Searches Across 6 Subreddits:**

| Subreddit | Queries | Posts |
|-----------|---------|-------|
| r/teslamotors | "optimus", "tesla robot", "humanoid robot" | 200 |
| r/robotics | "tesla optimus", "optimus robot" | 150 |
| r/technology | "tesla optimus", "optimus robot" | 150 |
| r/Futurology | "tesla optimus", "optimus humanoid" | 150 |
| r/artificial | "tesla optimus", "optimus robot" | 100 |
| r/RealTesla | "optimus" | 100 |

**Total:** ~850 posts → ~2,000-3,000 items (posts + comments)

### Output Files

- `optimus_data/optimus_reddit_OVERNIGHT_YYYYMMDD_HHMMSS.csv` - Full dataset
- `optimus_data/optimus_reddit_OVERNIGHT_sample.csv` - First 100 items

### Continuation Script

If collection is interrupted or rate-limited:

```bash
python reddit_continuation_scraper.py
```

Loads existing data and continues from where it stopped.

## Data Structure

CSV columns:
- `type`: "post" or "comment"
- `title`: Post title or comment reference
- `text`: Post body or comment text
- `combined_text`: Title + text (for analysis)
- `author`: Reddit username
- `score`: Upvotes
- `num_comments`: Comment count (posts only)
- `url`: Reddit URL
- `search_query`: Which search found this item
- `subreddit`: Source subreddit
- `date_scraped`: Timestamp
- `text_length`: Character count
- `has_metaphor`: Boolean flag for metaphor keywords

## Configuration

Edit search configurations in `reddit_overnight_scraper_3min.py`:

```python
search_configs = [
    {'subreddit': 'teslamotors', 'query': 'optimus', 'limit': 100},
    # Add more searches...
]
```

Adjust wait time between searches:
```python
time.sleep(180)  # 180 seconds = 3 minutes
```

## Rate Limiting

Reddit's public JSON API has rate limits (~60 requests/minute). This scraper:
- Waits 3 minutes between searches
- Waits 2 seconds between posts
- Should complete without errors

If you get 429 errors, increase wait time to 5 minutes.

## Research Use

This tool was developed for academic research analyzing metaphorical language in user discussions of AI/robotics. Collected data is processed through:

1. **Collection**: This scraper
2. **Metaphor detection**: Google Gemini Batch API
3. **Analysis**: Categorization into 6 metaphor types (Animate, Social, Service, Magical, Authority, Object)

See companion repository for Gemini processing pipeline.

## Ethical Considerations

- Uses Reddit's public JSON API (no authentication required)
- Collects only publicly available data
- Respects rate limits
- For academic research purposes
- Anonymizes data in publications

## Requirements

- Python 3.8+
- `requests` library
- `pandas` library

## Time Estimates

- **Setup**: 2 minutes
- **Collection**: 36-60 minutes
- **Expected output**: 2,000-3,000 items
- **Metaphor yield**: ~300-500 instances (at 16% detection rate)

## Troubleshooting

**Error 429 (Too Many Requests)**
- Increase wait time to 5 minutes: `time.sleep(300)`

**No posts found**
- Normal for some queries - Reddit may have limited results
- Other searches will compensate

**Script stops unexpectedly**
- Press Ctrl+C to save progress
- Use continuation script to resume

## License

MIT License - See LICENSE file

## Citation

If you use this scraper in academic work:

```
[Your citation format here]
```

## Contact

- Website: [www.mrsarkheh.com](https://www.mrsarkheh.com)
- Company: [www.mimradigital.com](https://www.mimradigital.com)

## Acknowledgments

Part of research project on Metaphor Hacking methodology applied to home AI and robotic companions.
