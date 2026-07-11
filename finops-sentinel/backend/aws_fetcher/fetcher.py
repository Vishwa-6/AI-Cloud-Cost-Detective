from typing import Any, Dict
from .base import AWSDataSource
from .mock_source import MockDataSource
from .live_source import LiveAWSDataSource

def get_data_source(mode: str) -> AWSDataSource:
    if mode == "mock":
        return MockDataSource()
    elif mode == "live":
        return LiveAWSDataSource()
    else:
        raise ValueError(f"Unknown mode: '{mode}'. Must be 'mock' or 'live'.")

def fetch_all_resources(mode: str) -> Dict[str, Any]:
    source = get_data_source(mode)
    return {
        "ec2_instances": source.get_ec2_instances(),
        "ebs_volumes": source.get_ebs_volumes(),
        "elastic_ips": source.get_elastic_ips(),
        "rds_instances": source.get_rds_instances(),
        "load_balancers": source.get_load_balancers(),
        "target_health": source.get_target_health(),
        "s3_buckets": source.get_s3_buckets(),
        "ec2_metrics": source.get_ec2_metrics(),
        "ec2_amis": source.get_ec2_amis(),
        "ebs_snapshots": source.get_ebs_snapshots(),
        "security_groups": source.get_security_groups(),
        "cw_log_groups": source.get_cw_log_groups(),
        "nat_gateways": source.get_nat_gateways(),
        "rds_metrics": source.get_rds_metrics(),
        "dynamodb_tables": source.get_dynamodb_tables(),
        "s3_metrics": source.get_s3_metrics(),
        "savings_plans": source.get_savings_plans()
    }
