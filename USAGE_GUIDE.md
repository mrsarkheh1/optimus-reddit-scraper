# Usage Guide

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
python reddit_overnight_scraper_3min.py

# 3. Type 'y' when prompted
Ready to start overnight collection? (y/N): y

# 4. Wait ~40 minutes
# 5. Find data in optimus_data/ folder
```

## Understanding the Output

### Expected Results

After full run:
- **Items**: 2,000-3,000 (posts + comments)
- **Posts**: ~200-400
- **Comments**: ~1,600-2,400
- **Subreddits**: 6 different communities
- **Metaphor signals**: ~25-30% of items

### Sample Output

```
Posts: 245
Comments: 1,758
Total items: 2,003
Metaphor signals: 587 (29.3%)
```

## Common Scenarios

### Scenario 1: Rate Limited (Error 429)

**Problem**: Script stops with "429 Client Error: Too Many Requests"

**Solution**: 
```bash
# Use continuation script
python reddit_continuation_scraper.py
```

Or increase wait time in main script:
```python
time.sleep(300)  # 5 minutes instead of 3
```

### Scenario 2: Want Different Subreddits

Edit `search_configs` in script:

```python
search_configs = [
    {'subreddit': 'YOUR_SUBREDDIT', 'query': 'YOUR_QUERY', 'limit': 100},
]
```

### Scenario 3: Test Run First

Modify script for quick test:

```python
# Reduce to 2 searches, 10 posts each
search_configs = [
    {'subreddit': 'teslamotors', 'query': 'optimus', 'limit': 10},
    {'subreddit': 'robotics', 'query': 'tesla optimus', 'limit': 10},
]

# Reduce wait time for testing
time.sleep(10)  # 10 seconds
```

Should complete in ~5 minutes with ~20-50 items.

### Scenario 4: Interrupted Collection

**If you stopped the script:**

Progress is auto-saved! Check `optimus_data/overnight_progress.csv`

**To continue:**
```bash
python reddit_continuation_scraper.py
```

## Data Analysis Tips

### Load Data in Python

```python
import pandas as pd

df = pd.read_csv('optimus_data/optimus_reddit_OVERNIGHT_20250101_123456.csv')

# Basic stats
print(f"Total items: {len(df)}")
print(f"Posts: {len(df[df['type'] == 'post'])}")
print(f"Comments: {len(df[df['type'] == 'comment'])}")

# Metaphor candidates
metaphors = df[df['has_metaphor'] == True]
print(f"Items with metaphor signals: {len(metaphors)}")

# By subreddit
print(df['subreddit'].value_counts())

# Sample metaphor-rich comments
print(metaphors[metaphors['type'] == 'comment']['text'].head(10))
```

### Filter for Quality

```python
# High-engagement items only
high_quality = df[df['score'] > 10]

# Longer comments (more likely to have rich metaphors)
detailed = df[df['text_length'] > 100]

# Combine
quality_metaphors = df[
    (df['has_metaphor'] == True) & 
    (df['score'] > 5) & 
    (df['text_length'] > 80)
]
```

## Customization Examples

### Focus on One Subreddit

```python
search_configs = [
    {'subreddit': 'teslamotors', 'query': 'optimus', 'limit': 100},
    {'subreddit': 'teslamotors', 'query': 'tesla robot', 'limit': 100},
    {'subreddit': 'teslamotors', 'query': 'humanoid robot', 'limit': 100},
    {'subreddit': 'teslamotors', 'query': 'optimus gen 2', 'limit': 100},
]
```

### Search Multiple Keywords

```python
keywords = ['optimus', 'tesla robot', 'humanoid', 'optimus gen 2']

search_configs = [
    {'subreddit': 'teslamotors', 'query': kw, 'limit': 100}
    for kw in keywords
]
```

### Different Sort Methods

Reddit supports: `comments`, `top`, `new`, `hot`

Modify the search method:
```python
params = {
    'q': query,
    'restrict_sr': 'on',
    'sort': 'top',  # Change from 'comments' to 'top'
    'limit': min(limit, 100),
    't': 'year'  # Add time filter: hour, day, week, month, year, all
}
```

## Best Practices

1. **Start with test run** (2 searches, 10 posts each)
2. **Run during off-peak hours** (late night/early morning)
3. **Check progress file** periodically
4. **Don't modify** while running
5. **Keep wait times** at 3+ minutes

## Performance Expectations

| Searches | Wait Time | Duration | Expected Items |
|----------|-----------|----------|----------------|
| 2 (test) | 10 sec | 5 min | 20-50 |
| 5 | 3 min | 20 min | 500-800 |
| 12 (full) | 3 min | 40 min | 2,000-3,000 |
| 12 (full) | 5 min | 60 min | 2,000-3,000 |

## Troubleshooting

**"No posts found"**
- Normal - not all queries return results
- Other searches compensate

**Script freezes**
- Reddit might be slow
- Wait or press Ctrl+C to save progress

**Low item counts**
- Some posts have few comments (normal)
- Check if queries are too specific
- Try broader terms

**Duplicate data**
- Don't re-run full script on same day
- Use continuation script instead
- Deduplication happens automatically

## Next Steps

After collection:
1. Review CSV in Excel/Pandas
2. Convert to JSONL for LLM processing
3. Run through metaphor detection (Gemini API)
4. Analyze results by category

## Support

Questions? Check:
- Main README.md for overview
- Script comments for technical details
- GitHub Issues for known problems
