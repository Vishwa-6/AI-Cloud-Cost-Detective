import json
import os
from pathlib import Path
from typing import Any, Dict, List
from .base import AWSDataSource

class MockDataSource(AWSDataSource):
    def __init__(self):
        # Resolve mock_data directory relative to project root
        self.mock_dir = Path(__file__).parent.parent.parent / "mock_data"

    def _read_json(self, filename: str) -> Any:
        file_path = self.mock_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Mock file missing: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_ec2_instances(self) -> Dict[str, Any]:
        return self._read_json("ec2_instances.json")

    def get_ebs_volumes(self) -> Dict[str, Any]:
        return self._read_json("ebs_volumes.json")

    def get_elastic_ips(self) -> Dict[str, Any]:
        return self._read_json("elastic_ips.json")

    def get_rds_instances(self) -> Dict[str, Any]:
        return self._read_json("rds_instances.json")

    def get_load_balancers(self) -> Dict[str, Any]:
        return self._read_json("load_balancers.json")

    def get_target_health(self) -> Dict[str, Any]:
        return self._read_json("target_health.json")

    def get_s3_buckets(self) -> Dict[str, Any]:
        return self._read_json("s3_buckets.json")

    def get_ec2_metrics(self) -> List[Dict[str, Any]]:
        return self._read_json("ec2_metrics.json")

    def get_ec2_amis(self) -> Dict[str, Any]:
        return self._read_json("ec2_amis.json")

    def get_ebs_snapshots(self) -> Dict[str, Any]:
        return self._read_json("ebs_snapshots.json")

    def get_security_groups(self) -> Dict[str, Any]:
        return self._read_json("security_groups.json")

    def get_cw_log_groups(self) -> Dict[str, Any]:
        return self._read_json("cw_log_groups.json")

    def get_nat_gateways(self) -> Dict[str, Any]:
        return self._read_json("nat_gateways.json")

    def get_rds_metrics(self) -> List[Dict[str, Any]]:
        return self._read_json("rds_metrics.json")

    def get_dynamodb_tables(self) -> Dict[str, Any]:
        return self._read_json("dynamodb_tables.json")

    def get_s3_metrics(self) -> List[Dict[str, Any]]:
        return self._read_json("s3_metrics.json")

    def get_savings_plans(self) -> Dict[str, Any]:
        return self._read_json("savings_plans.json")
