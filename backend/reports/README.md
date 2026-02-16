# Analysis Reports Directory

This directory stores all analysis reports automatically for easy reference and troubleshooting.

## How It Works

Every time an analysis is run (image, video, Figma, URL, PDF), the complete report is automatically saved here as a JSON file.

## File Naming

Reports are saved with timestamps:
- Format: `report_YYYY-MM-DD_HH-MM-SS_{type}.json`
- Example: `report_2024-02-15_14-30-45_url.json`

Analysis types:
- `single_image` - Single screenshot analysis
- `multi_image` - Multiple screenshots
- `video` - Video analysis
- `figma` - Figma file analysis
- `url` - Website crawl analysis
- `pdf` - PDF document analysis

## What's in a Report

Each report contains:
```json
{
  "timestamp": "2024-02-15T14:30:45.123456",
  "timestamp_readable": "2024-02-15 14:30:45",
  "analysis_type": "url",
  "user_context": {
    "users": "...",
    "tasks": "...",
    "format": "...",
    "content_type": "..."
  },
  "metadata": {
    "url": "https://example.com",
    "pages_analyzed": 5,
    ...
  },
  "analysis_result": {
    "html": "...",
    "statistics": {...},
    "site_summary": {...},
    "page_analyses": [...],
    ...
  }
}
```

## Using Reports for Troubleshooting

### In Claude Code Chat

Instead of copy-pasting the entire report, you can now:

1. **List recent reports:**
   ```bash
   curl http://localhost:8000/reports
   ```

2. **Reference a specific report:**
   - Find the filename from the list (e.g., `report_2024-02-15_14-30-45_url.json`)
   - Tell Claude: "Check the report from today at 2:30pm" or "Look at report_2024-02-15_14-30-45_url.json"
   - Claude can read the file directly using the Read tool

3. **Get report via API:**
   ```bash
   curl http://localhost:8000/reports/report_2024-02-15_14-30-45_url.json
   ```

### Direct File Access

You can also open the JSON files directly in VSCode or any text editor:
- Full path: `c:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend\reports\`
- Use VSCode's JSON formatting (Shift+Alt+F) for easier reading

## Maintenance

Reports are kept indefinitely by default. You can manually delete old reports, or implement cleanup:

```python
from src.report_saver import get_report_saver

# Keep only the 50 most recent reports
saver = get_report_saver()
saver.cleanup_old_reports(keep_count=50)
```

## Privacy Note

Reports may contain:
- User-provided context
- Analysis results
- URLs and file names
- Partial API keys (first 8 characters for identification)

Reports are **not committed to git** (listed in `.gitignore`).
