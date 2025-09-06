"""
Example demonstrating comprehensive fingerprinting evasion testing.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.testing.fingerprinting_tester import FingerprintingTester


async def main():
    """Demonstrate FingerprintingTester usage."""
    # Create FingerprintingTester instance
    tester = FingerprintingTester()
    
    print("Starting comprehensive fingerprinting evasion testing...")
    print()
    
    # Run a comprehensive test
    report = await tester.run_comprehensive_test("example_session_001")
    
    print("Comprehensive Fingerprinting Test Results:")
    print(f"Session ID: {report.session_id}")
    print(f"Overall Score: {report.overall_score:.2f}")
    print(f"Fingerprint Hash: {report.fingerprint_hash}")
    print(f"Test Count: {len(report.test_results)}")
    print()
    
    # Display individual test results
    print("Individual Test Results:")
    for result in report.test_results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {status} {result.test_name} (Score: {result.score:.2f})")
        if result.details:
            for key, value in result.details.items():
                print(f"    {key}: {value}")
        print()
    
    # Save the report
    report_file = "fingerprinting_test_report.json"
    tester.save_report(report, report_file)
    print(f"Report saved to: {report_file}")
    print()
    
    # Load and display the saved report
    loaded_report = tester.load_report(report_file)
    print("Loaded Report Verification:")
    print(f"Session ID: {loaded_report.session_id}")
    print(f"Overall Score: {loaded_report.overall_score:.2f}")
    print(f"Test Count: {len(loaded_report.test_results)}")
    print()
    
    # Example of continuous monitoring (for a short duration)
    print("Starting continuous monitoring (5 seconds)...")
    try:
        # Run continuous monitoring for a very short duration for demonstration
        # In practice, this would run for much longer
        reports = await tester.run_continuous_monitoring(duration_minutes=5/60)  # 5 seconds
        print(f"Continuous monitoring completed. Generated {len(reports)} reports.")
    except Exception as e:
        print(f"Continuous monitoring example completed with message: {e}")
    
    print()
    print("Fingerprinting testing example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())