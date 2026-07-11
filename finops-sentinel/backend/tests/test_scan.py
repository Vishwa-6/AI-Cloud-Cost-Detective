import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
from aws_fetcher.fetcher import fetch_all_resources
from analysis.analyzer import analyze_resources

async def run_test():
    data = fetch_all_resources("mock")
    print(f"Keys in data: {list(data.keys())}")
    for k, v in data.items():
        print(f" - {k}: {len(v)} items")
    result = analyze_resources(data)
    
    print(f"Total Resources Scanned: {result['summary']['total_resources_scanned']}")
    print(f"Total Issues Found: {result['summary']['total_issues_found']}")
    print(f"Total Savings: ${result['summary']['total_estimated_monthly_savings_usd']}")
    print("\nFindings:")
    for f in result.get('findings', []):
        print(f" - {f['resource_id']}: {f['issue']}")

if __name__ == "__main__":
    asyncio.run(run_test())
