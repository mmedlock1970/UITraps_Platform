# Cookie Authentication Guide for Web Crawling

## Overview

UITraps Platform supports crawling authenticated websites by providing cookies. This allows the analyzer to see the same content you see when logged in, preventing false positives from missing authenticated elements.

## Why Use Cookie Authentication?

Without cookies, the crawler sees the logged-out version of websites, which can lead to:
- **False positives**: Elements that only appear when logged in are reported as "missing" or "invisible"
- **Incomplete analysis**: Can't access pages that require authentication
- **Incorrect context**: Analyzer doesn't see personalized content, user dashboards, etc.

## Method 1: Export Cookies from Browser (Recommended)

### Chrome/Edge

1. **Install Extension**: Install the "[EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie)" extension
2. **Navigate**: Go to the authenticated page you want to analyze (log in first)
3. **Export**: Click the EditThisCookie icon in your toolbar
4. **Copy JSON**: Click "Export" button → Select "JSON format" → Copy the JSON array

Example output:
```json
[
  {
    "domain": ".amazon.com",
    "expirationDate": 1738425600,
    "hostOnly": false,
    "httpOnly": false,
    "name": "session-id",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "abc-123-def-456",
    "id": 1
  }
]
```

### Firefox

1. **Install Extension**: Install the "[Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)" extension
2. **Navigate**: Go to the authenticated page (log in first)
3. **Export**: Click the Cookie-Editor icon → Click "Export" tab
4. **Copy**: Select "JSON" format → Click "Export" → Copy the JSON

### Safari

1. **Use Developer Tools**: Open Developer Tools (Cmd+Option+I)
2. **Go to Storage**: Click "Storage" tab → Cookies → Select your site
3. **Manually copy cookies** or use browser console:
   ```javascript
   copy(document.cookie)
   ```

## Method 2: Playwright Storage State (Advanced)

For complete authentication including localStorage and sessionStorage:

### Save Storage State

Create a script to log in and save the state:

```javascript
// save-auth.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Navigate to login page
  await page.goto('https://yoursite.com/login');

  // Wait for manual login
  console.log('Please log in, then press Enter in the terminal...');
  await page.pause();  // Manual login

  // Save the authenticated state
  await context.storageState({ path: 'auth.json' });

  await browser.close();
  console.log('✅ Authentication saved to auth.json');
})();
```

Run it:
```bash
node save-auth.js
```

### Use Storage State

Currently, the API accepts cookies directly. To use storage_state files, extract cookies from the JSON:

```javascript
// extract-cookies.js
const fs = require('fs');
const authState = JSON.parse(fs.readFileSync('auth.json', 'utf-8'));
console.log(JSON.stringify(authState.cookies));
```

## Using Cookies with UITraps Platform

### Via API

```bash
curl -X POST http://localhost:8000/analyze-url \
  -F 'url=https://app.example.com/dashboard' \
  -F 'users=Team members' \
  -F 'tasks=Reviewing reports' \
  -F 'format=Web application' \
  -F 'api_key=YOUR_API_KEY' \
  -F 'max_pages=5' \
  -F 'cookies=[{"name":"session","value":"abc123","domain":".example.com"}]'
```

### Via Frontend

The frontend will need to be updated to accept cookie input. For now, use the API directly or modify the frontend to include cookies in the request.

### Cookie Format

The `cookies` parameter accepts a JSON string in multiple formats:

**Array format** (from browser extensions):
```json
[
  {"name": "session-id", "value": "abc123", "domain": ".amazon.com"},
  {"name": "user-token", "value": "xyz789", "domain": ".amazon.com"}
]
```

**Object format** (domain-grouped):
```json
{
  "amazon.com": [
    {"name": "session-id", "value": "abc123"},
    {"name": "user-token", "value": "xyz789"}
  ]
}
```

**Single cookie** (simplified):
```json
{"name": "session-id", "value": "abc123"}
```

The crawler will automatically:
- Parse any of these formats
- Add missing domain/URL fields based on the target URL
- Validate and sanitize cookie values

## Security Considerations

### Important Warnings

⚠️ **Never commit cookies to git**: Cookies contain sensitive session data that can be used to impersonate you

⚠️ **Cookies expire**: Re-export periodically (usually after logout or session expiration)

⚠️ **Secure transmission**: Only use over HTTPS or localhost

⚠️ **Limited sharing**: Only share cookies with trusted systems/people

### Best Practices

1. **Use environment variables** for sensitive cookie values in scripts:
   ```bash
   export CRAWLER_COOKIES='[{"name":"session","value":"..."}]'
   ```

2. **Rotate cookies frequently**: Export fresh cookies before each analysis

3. **Use read-only accounts**: If possible, use an account with read-only permissions

4. **Monitor usage**: Check for unauthorized access to your account

5. **Clear after use**: Cookies are temporary - they're not persisted beyond the crawl

## Troubleshooting

### Cookies not working

**Problem**: Crawler still sees logged-out version

**Solutions**:
- Verify cookies are from the exact domain being crawled
- Check cookie hasn't expired (look at `expirationDate` field)
- Ensure you're using `domain` field with leading dot (`.example.com` not `example.com`)
- Try exporting cookies again after fresh login

### "Failed to add cookies" error

**Problem**: Console shows cookie injection failed

**Solutions**:
- Verify JSON syntax is valid
- Check for special characters in cookie values (quotes, newlines)
- Ensure cookie has `name` and `value` fields minimum
- Try simplified format: `[{"name":"session","value":"abc123"}]`

### Sensitive pages blocked

**Problem**: Even with cookies, some pages return 403/401

**Solutions**:
- Check if site uses additional authentication (2FA, CSRF tokens)
- Verify cookies include all required authentication tokens
- Site may detect automated browsing - try setting user-agent string
- Some sites require interactive login (can't be automated)

## Example: Amazon.com

To analyze your authenticated Amazon.com experience:

1. **Log in to Amazon** in your browser
2. **Export cookies** using EditThisCookie
3. **Run analysis** with cookies:

```bash
curl -X POST http://localhost:8000/analyze-url \
  -F 'url=https://www.amazon.com' \
  -F 'users=Online shoppers' \
  -F 'tasks=Finding and purchasing products' \
  -F 'api_key=YOUR_KEY' \
  -F 'cookies@exported-amazon-cookies.json'
```

4. **Review report** - should now show personalized elements like:
   - "Hello, [Your Name]" greeting
   - Account menu
   - Order history links
   - Personalized recommendations

Without cookies, the analyzer might report these as "invisible elements" since they don't appear when logged out.

## Privacy & Data Handling

- Cookies are **only used during the crawl** - not stored long-term
- Cookies are **passed directly to Playwright** - not logged or persisted
- Screenshots captured **may include personal data** from authenticated pages
- Reports are **saved locally** - review before sharing

## Next Steps

- See [REPORT_REFERENCE_GUIDE.md](../REPORT_REFERENCE_GUIDE.md) for troubleshooting reports
- Check [README.md](../README.md) for general platform documentation
- Report cookie-related issues on [GitHub](https://github.com/mmedlock1970/UITraps_Platform/issues)
