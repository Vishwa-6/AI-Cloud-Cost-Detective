from abc import ABC, abstractmethod
from typing import Any, Dict, List

class AWSDataSource(ABC):
    @abstractmethod
    def get_ec2_instances(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_ebs_volumes(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_elastic_ips(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_rds_instances(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_load_balancers(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_target_health(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_s3_buckets(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_ec2_metrics(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_ec2_amis(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_ebs_snapshots(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_security_groups(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_cw_log_groups(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_nat_gateways(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_rds_metrics(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_dynamodb_tables(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_s3_metrics(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_savings_plans(self) -> Dict[str, Any]:
        pass
