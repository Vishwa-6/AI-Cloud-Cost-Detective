import os
import boto3
from typing import Any, Dict, List
from datetime import datetime, timedelta, timezone
from .base import AWSDataSource

class AWSFetchError(Exception):
    pass

class LiveAWSDataSource(AWSDataSource):
    def __init__(self):
        region = os.environ.get("AWS_REGION", "ap-south-1")
        try:
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.rds_client = boto3.client('rds', region_name=region)
            self.elbv2_client = boto3.client('elbv2', region_name=region)
            self.s3_client = boto3.client('s3', region_name=region)
            self.cw_client = boto3.client('cloudwatch', region_name=region)
            self.logs_client = boto3.client('logs', region_name=region)
            self.dynamodb_client = boto3.client('dynamodb', region_name=region)
            self.ce_client = boto3.client('ce', region_name=region)
        except Exception as e:
            raise AWSFetchError(f"Failed to initialize boto3 clients: {str(e)}")

    def get_ec2_instances(self) -> Dict[str, Any]:
        try:
            paginator = self.ec2_client.get_paginator('describe_instances')
            reservations = []
            for page in paginator.paginate():
                reservations.extend(page.get('Reservations', []))
            return {"Reservations": reservations}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch EC2 instances: {str(e)}")

    def get_ebs_volumes(self) -> Dict[str, Any]:
        try:
            paginator = self.ec2_client.get_paginator('describe_volumes')
            volumes = []
            for page in paginator.paginate():
                volumes.extend(page.get('Volumes', []))
            return {"Volumes": volumes}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch EBS volumes: {str(e)}")

    def get_elastic_ips(self) -> Dict[str, Any]:
        try:
            response = self.ec2_client.describe_addresses()
            return {"Addresses": response.get('Addresses', [])}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch Elastic IPs: {str(e)}")

    def get_rds_instances(self) -> Dict[str, Any]:
        try:
            paginator = self.rds_client.get_paginator('describe_db_instances')
            db_instances = []
            for page in paginator.paginate():
                db_instances.extend(page.get('DBInstances', []))
            return {"DBInstances": db_instances}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch RDS instances: {str(e)}")

    def get_load_balancers(self) -> Dict[str, Any]:
        try:
            paginator = self.elbv2_client.get_paginator('describe_load_balancers')
            load_balancers = []
            for page in paginator.paginate():
                load_balancers.extend(page.get('LoadBalancers', []))
            return {"LoadBalancers": load_balancers}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch Load Balancers: {str(e)}")

    def get_target_health(self) -> Dict[str, Any]:
        try:
            target_health_data = {}
            lbs_paginator = self.elbv2_client.get_paginator('describe_load_balancers')
            for lb_page in lbs_paginator.paginate():
                for lb in lb_page.get('LoadBalancers', []):
                    lb_name = lb.get('LoadBalancerName')
                    lb_arn = lb.get('LoadBalancerArn')
                    
                    tgs = self.elbv2_client.describe_target_groups(LoadBalancerArn=lb_arn).get('TargetGroups', [])
                    
                    health_descriptions = []
                    for tg in tgs:
                        tg_arn = tg.get('TargetGroupArn')
                        health = self.elbv2_client.describe_target_health(TargetGroupArn=tg_arn).get('TargetHealthDescriptions', [])
                        health_descriptions.extend(health)
                        
                    target_health_data[lb_name] = {"TargetHealthDescriptions": health_descriptions}
            return target_health_data
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch Target Health: {str(e)}")

    def get_s3_buckets(self) -> Dict[str, Any]:
        try:
            response = self.s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            for bucket in buckets:
                try:
                    self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket['Name'])
                    bucket['lifecycle_configured'] = True
                except Exception:
                    bucket['lifecycle_configured'] = False
            return {"Buckets": buckets}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch S3 Buckets: {str(e)}")

    def get_ec2_metrics(self) -> List[Dict[str, Any]]:
        try:
            instances = self.get_ec2_instances()
            metrics = []
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=1)
            
            for res in instances.get("Reservations", []):
                for inst in res.get("Instances", []):
                    instance_id = inst.get("InstanceId")
                    if not instance_id:
                        continue
                        
                    stats = self.cw_client.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400, # 24 hours
                        Statistics=['Average']
                    )
                    
                    datapoints = stats.get('Datapoints', [])
                    avg_cpu = datapoints[0].get('Average', 0.0) if datapoints else 0.0
                    
                    metrics.append({
                        "instance_id": instance_id,
                        "avg_cpu_utilization_percent": avg_cpu
                    })
            return metrics
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch EC2 Metrics: {str(e)}")

    def get_ec2_amis(self) -> Dict[str, Any]:
        try:
            response = self.ec2_client.describe_images(Owners=['self'])
            return {"Images": response.get('Images', [])}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch EC2 AMIs: {str(e)}")

    def get_ebs_snapshots(self) -> Dict[str, Any]:
        try:
            paginator = self.ec2_client.get_paginator('describe_snapshots')
            snapshots = []
            for page in paginator.paginate(OwnerIds=['self']):
                snapshots.extend(page.get('Snapshots', []))
            return {"Snapshots": snapshots}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch EBS Snapshots: {str(e)}")

    def get_security_groups(self) -> Dict[str, Any]:
        try:
            paginator = self.ec2_client.get_paginator('describe_security_groups')
            sgs = []
            for page in paginator.paginate():
                sgs.extend(page.get('SecurityGroups', []))
            return {"SecurityGroups": sgs}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch Security Groups: {str(e)}")

    def get_cw_log_groups(self) -> Dict[str, Any]:
        try:
            paginator = self.logs_client.get_paginator('describe_log_groups')
            log_groups = []
            for page in paginator.paginate():
                log_groups.extend(page.get('logGroups', []))
            return {"logGroups": log_groups}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch CloudWatch Log Groups: {str(e)}")

    def get_nat_gateways(self) -> Dict[str, Any]:
        try:
            paginator = self.ec2_client.get_paginator('describe_nat_gateways')
            nat_gateways = []
            for page in paginator.paginate():
                nat_gateways.extend(page.get('NatGateways', []))
            return {"NatGateways": nat_gateways}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch NAT Gateways: {str(e)}")

    def get_rds_metrics(self) -> List[Dict[str, Any]]:
        try:
            instances = self.get_rds_instances()
            metrics = []
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=1)
            
            for db in instances.get("DBInstances", []):
                db_id = db.get("DBInstanceIdentifier")
                if not db_id: continue
                
                stats = self.cw_client.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='FreeStorageSpace',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
                    StartTime=start_time, EndTime=end_time, Period=86400, Statistics=['Average']
                )
                datapoints = stats.get('Datapoints', [])
                avg_free = datapoints[0].get('Average', 0.0) if datapoints else 0.0
                metrics.append({"DBInstanceIdentifier": db_id, "FreeStorageSpace": avg_free})
            return metrics
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch RDS Metrics: {str(e)}")

    def get_dynamodb_tables(self) -> Dict[str, Any]:
        try:
            paginator = self.dynamodb_client.get_paginator('list_tables')
            tables = []
            for page in paginator.paginate():
                for table_name in page.get('TableNames', []):
                    desc = self.dynamodb_client.describe_table(TableName=table_name)
                    tables.append(desc.get('Table', {}))
            return {"Tables": tables}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch DynamoDB Tables: {str(e)}")

    def get_s3_metrics(self) -> List[Dict[str, Any]]:
        try:
            buckets = self.get_s3_buckets()
            metrics = []
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=2)
            
            for b in buckets.get("Buckets", []):
                name = b.get("Name")
                if not name: continue
                stats = self.cw_client.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[{'Name': 'BucketName', 'Value': name}, {'Name': 'StorageType', 'Value': 'StandardStorage'}],
                    StartTime=start_time, EndTime=end_time, Period=86400, Statistics=['Average']
                )
                datapoints = stats.get('Datapoints', [])
                size_bytes = datapoints[0].get('Average', 0.0) if datapoints else 0.0
                metrics.append({"BucketName": name, "BucketSizeBytes": size_bytes})
            return metrics
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch S3 Metrics: {str(e)}")

    def get_savings_plans(self) -> Dict[str, Any]:
        try:
            end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
            response = self.ce_client.get_savings_plans_coverage(
                TimePeriod={'Start': start_date, 'End': end_date}
            )
            return {"SavingsPlansCoverages": response.get('SavingsPlansCoverages', [])}
        except Exception as e:
            raise AWSFetchError(f"Failed to fetch Savings Plans Coverage: {str(e)}")
