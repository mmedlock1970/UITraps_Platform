# Report Reference Guide

## Problem Solved ✓

You no longer need to copy-paste entire analysis reports when troubleshooting! Every analysis is now automatically saved to disk, and you can simply reference the file.

## How It Works

### Automatic Saving

Every time you run an analysis (image, video, Figma, URL, PDF), the complete report is automatically saved to:

```
backend/reports/report_YYYY-MM-DD_HH-MM-SS_{type}.json
```

Example: `backend/reports/report_2026-02-15_14-30-45_url.json`

### What's Saved

Each report contains:
- **Timestamp**: When the analysis was run
- **Analysis type**: single_image, multi_image, video, figma, url, pdf
- **User context**: Users, tasks, format descriptions
- **Full analysis results**: Statistics, issues, recommendations, HTML report
- **Metadata**: File names, URLs, page counts, etc.

## Using Reports for Troubleshooting

### Method 1: Direct File Reference (Recommended)

When working with Claude Code, just reference the report file:

**Instead of this:**
```
[Pasting 50KB of JSON report data...]
Can you help me understand why trap X was detected?
```

**Do this:**
```
Can you check the report from today at 2:30pm?
I want to understand why the "Invisible Element" trap was detected.
```

Or even simpler:
```
Look at the latest URL analysis report and explain the critical issues.
```

Claude Code can:
- List reports in the directory
- Read specific report files
- Search through reports
- Compare multiple reports

### Method 2: API Endpoints

You can also use the new API endpoints:

**List recent reports:**
```bash
curl http://localhost:8000/reports
```

Response:
```json
{
  "success": true,
  "reports": [
    {
      "filename": "report_2026-02-15_14-30-45_url.json",
      "timestamp": "2026-02-15 14:30:45",
      "analysis_type": "url",
      "url": "https://example.com",
      "pages_analyzed": 5,
      "file_size_kb": 125.3
    }
  ]
}
```

**Get specific report:**
```bash
curl http://localhost:8000/reports/report_2026-02-15_14-30-45_url.json
```

### Method 3: Direct File Access

Open the JSON file in VSCode or any text editor:

1. Navigate to: `backend/reports/`
2. Open the report file
3. Use Shift+Alt+F to format the JSON
4. Review the analysis results

## Example Troubleshooting Workflows

### Scenario 1: Understanding a specific trap detection

**You:**
> "Check the latest Figma analysis report. Why was 'Ambiguous Home' detected on the dashboard page?"

**Claude Code will:**
1. List reports in `backend/reports/`
2. Find the latest Figma analysis
3. Read the report file
4. Search for "Ambiguous Home" trap
5. Find the specific page analysis
6. Explain the detection reasoning

### Scenario 2: Comparing two analyses

**You:**
> "Compare the URL analysis from yesterday vs today. Did the changes reduce the critical issues?"

**Claude Code will:**
1. Find both report files
2. Read statistics from each
3. Compare critical issue counts
4. Show what changed

### Scenario 3: Investigating unexpected results

**You:**
> "The report from 2pm showed 10 critical issues but I only expected 2. What are the other 8?"

**Claude Code will:**
1. Find the report from 2pm
2. Read the full analysis
3. List all 10 critical issues
4. Explain each detection

## Report Structure

Here's what's inside each report:

```json
{
  "timestamp": "2026-02-15T14:30:45.123456",
  "timestamp_readable": "2026-02-15 14:30:45",
  "analysis_type": "url",

  "user_context": {
    "users": "First-time visitors, ages 25-45",
    "tasks": "Sign up for an account, Browse products",
    "format": "Website",
    "content_type": "website"
  },

  "metadata": {
    "url": "https://example.com",
    "pages_analyzed": 5,
    "capture_interactions": false,
    "api_key": "sk_test_..."
  },

  "analysis_result": {
    "html": "<html>...",  // Full HTML report

    "statistics": {
      "total_issues": 12,
      "critical_count": 3,
      "moderate_count": 5,
      "minor_count": 4,
      "positive_count": 8
    },

    "site_summary": {
      "overall_assessment": "...",
      "page_roles_found": ["homepage", "product", "contact"],
      "incomplete_task_flows": [...],
      "sitewide_issues": [...]
    },

    "page_analyses": [
      {
        "page": {
          "url": "https://example.com",
          "title": "Homepage"
        },
        "analysis": {
          "report": {
            "critical_issues": [...],
            "moderate_issues": [...],
            "minor_issues": [...],
            "positive_observations": [...]
          }
        }
      }
    ],

    "recommendations": [...]
  }
}
```

## Maintenance

Reports are kept indefinitely by default. To clean up old reports:

```python
from src.report_saver import get_report_saver

saver = get_report_saver()
saver.cleanup_old_reports(keep_count=50)  # Keep only 50 most recent
```

Or manually delete old files from `backend/reports/`.

## Privacy & Security

- Reports are **not committed to git** (listed in `.gitignore`)
- Reports may contain user-provided context and analysis results
- API keys are truncated (only first 8 characters saved for identification)
- You can safely delete reports at any time

## Tips

1. **Use descriptive context**: The user_context in the report helps you remember what the analysis was about
2. **Check timestamps**: Reports are sorted by modification time (newest first)
3. **File size**: Large reports (>500KB) usually indicate multi-page or comprehensive analyses
4. **Analysis type**: Filter by type to find specific kinds of analyses (url, figma, pdf, etc.)

## Quick Reference Commands

```bash
# List all reports
ls backend/reports/

# List reports by date (newest first)
ls -lt backend/reports/

# Find reports by type
ls backend/reports/*_url.json
ls backend/reports/*_figma.json

# Count total reports
ls backend/reports/*.json | wc -l

# View latest report
cat "$(ls -t backend/reports/*.json | head -1)"
```

---

**You're all set!** Next time you run an analysis, the report will be automatically saved. Just reference it when troubleshooting instead of copy-pasting the whole thing.
