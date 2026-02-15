# Test Images

This directory should contain test images for fixture generation (Tier 2 tests).

## Required Images

Add the following 5 test images:

1. **simple_form.png**
   - Basic form with inputs and submit button
   - Example: Contact form, login form, signup form
   - Should have a few UI elements

2. **complex_dashboard.png**
   - Dense dashboard with multiple widgets
   - Example: Analytics dashboard, admin panel
   - Should have many UI elements

3. **mobile_screen.png**
   - Mobile app interface
   - Example: Mobile app screenshot
   - Should be mobile-sized (portrait)

4. **error_state.png**
   - Error screen or validation failure
   - Example: Form validation errors, 404 page
   - Should show error state

5. **minimal_ui.png**
   - Very simple UI with few elements
   - Example: Landing page, empty state
   - Should be minimalist

## How to Add Images

1. Take screenshots of real UIs or use test designs
2. Save as PNG format
3. Name exactly as above (case-sensitive)
4. Place in this directory

## After Adding Images

Run the fixture generation script:

```bash
cd backend
python tests/generate_fixtures.py
```

This will:
- Analyze each image using Claude API
- Save responses to `tests/fixtures/cached_analyses/`
- Cost: ~$0.05 per image = $0.25 total (one-time)

## Notes

- Images should be diverse to catch different edge cases
- Use real designs from your product or public websites
- Quality doesn't matter much - these are for structural testing
- Once fixtures are generated, you can delete images if needed
