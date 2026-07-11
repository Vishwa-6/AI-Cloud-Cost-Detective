# pyrefly: ignore [missing-import]
import pytest
from backend.aws_fetcher.fetcher import fetch_all_resources
from backend.analysis.rules_engine import run_all_rules

def test_rules_engine_mock_data():
    # Load all mock data (0 API calls)
    resource_data = fetch_all_resources('mock')
    
    # Run the deterministic rules engine
    findings = run_all_rules(resource_data)
    
    # Map findings by resource ID for easy asserting
    findings_map = {f['resource_id']: f for f in findings}
    
    # Check finding count (20 from before + 6 new = 26)
    assert len(findings) == 26, f"Expected exactly 26 findings, got {len(findings)}"
    
    # Check a few specific findings
    assert 'i-crit-idle' in findings_map, "Expected critical idle EC2"
    assert 'vol-crit-unattached' in findings_map, "Expected critical unattached EBS"
    assert 'db-crit-over' in findings_map, "Expected critical oversized RDS"
    
    # Check new 6 rules
    assert '/aws/lambda/forgotten-function' in findings_map, "Expected CloudWatch retention finding"
    assert 'nat-healthy' in findings_map, "Expected NAT gateway finding"
    assert 'db-crit-over' in findings_map, "Expected RDS storage finding (since it is massively overprovisioned)"
    assert 'idle-table' in findings_map, "Expected DynamoDB capacity finding"
    assert 'bucket-prod-crit' in findings_map, "Expected large S3 bucket finding"
    assert 'savings-plan' in findings_map, "Expected Savings Plans finding"
    
    # Assert healthy resources are NOT flagged
    assert 'i-healthy' not in findings_map, "Healthy EC2 should not be flagged"
    assert 'vol-healthy' not in findings_map, "Healthy EBS should not be flagged"
    assert 'db-healthy' not in findings_map, "Healthy RDS should not be flagged"
    assert '/aws/lambda/healthy-function' not in findings_map, "Healthy CloudWatch group should not be flagged"
    assert 'healthy-table' not in findings_map, "Healthy DynamoDB table should not be flagged"
