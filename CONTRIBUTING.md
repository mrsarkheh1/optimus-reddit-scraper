# Contributing

## How to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Make changes
4. Test thoroughly
5. Commit (`git commit -m 'Add improvement'`)
6. Push (`git push origin feature/improvement`)
7. Open Pull Request

## Development Setup

```bash
git clone https://github.com/yourusername/optimus-reddit-scraper.git
cd optimus-reddit-scraper
pip install -r requirements.txt
```

## Testing Changes

Before submitting:
1. Run test collection (2 searches, 10 posts)
2. Verify CSV output format
3. Check deduplication works
4. Test error handling

## Code Style

- Follow PEP 8
- Add docstrings to functions
- Comment complex logic
- Keep functions focused

## Areas for Improvement

- Add more subreddits
- Implement parallel requests
- Add sentiment analysis
- Export to other formats (JSON, Parquet)
- Web interface
- Real-time monitoring

## Reporting Issues

Include:
- Python version
- Error messages
- Steps to reproduce
- Expected vs actual behavior

## Questions

Open an issue or contact maintainers.
