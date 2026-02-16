"""
Quick test script for report saver functionality.

Run this to verify that reports are being saved correctly.
"""

from src.report_saver import save_analysis_report, get_report_saver

# Test saving a mock report
def test_report_saver():
    print("Testing report saver...")

    # Mock analysis result
    mock_result = {
        "html": "<h1>Test Report</h1>",
        "statistics": {
            "total_issues": 5,
            "critical_count": 2,
            "moderate_count": 2,
            "minor_count": 1
        },
        "site_summary": {
            "overall_assessment": "Test assessment",
            "critical_count": 2
        }
    }

    # Mock user context
    mock_context = {
        "users": "Test users",
        "tasks": "Test tasks",
        "format": "Test format"
    }

    # Mock metadata
    mock_metadata = {
        "url": "https://example.com",
        "pages_analyzed": 3
    }

    # Save the report
    print("Saving test report...")
    report_path = save_analysis_report(
        analysis_result=mock_result,
        analysis_type="url",
        user_context=mock_context,
        metadata=mock_metadata
    )

    print(f"[OK] Report saved to: {report_path}")

    # List reports
    print("\nListing saved reports...")
    saver = get_report_saver()
    reports = saver.list_reports(limit=5)

    print(f"[OK] Found {len(reports)} reports:")
    for report in reports:
        print(f"  - {report['filename']}")
        print(f"    Type: {report['analysis_type']}")
        print(f"    Time: {report['timestamp']}")
        if 'url' in report:
            print(f"    URL: {report['url']}")
        print()

    # Retrieve the report we just saved
    filename = report_path.split("\\")[-1]
    print(f"Retrieving report: {filename}")
    retrieved = saver.get_report(filename)

    if retrieved:
        print("[OK] Report retrieved successfully")
        print(f"  Analysis type: {retrieved['analysis_type']}")
        print(f"  Timestamp: {retrieved['timestamp_readable']}")
        print(f"  Critical issues: {retrieved['analysis_result']['statistics']['critical_count']}")
    else:
        print("[ERROR] Failed to retrieve report")

    print("\n[OK] All tests passed!")

if __name__ == "__main__":
    test_report_saver()
