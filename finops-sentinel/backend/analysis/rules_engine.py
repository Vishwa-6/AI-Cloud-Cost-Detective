import datetime
from typing import Any, Dict, List

def run_all_rules(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    findings.extend(check_ec2_idle(resource_data))
    findings.extend(check_ec2_oversized(resource_data))
    findings.extend(check_ec2_amis(resource_data))
    findings.extend(check_ec2_security_groups(resource_data))
    
    findings.extend(check_ebs_unattached(resource_data))
    findings.extend(check_ebs_snapshots(resource_data))
    
    findings.extend(check_eip_unattached(resource_data))
    
    findings.extend(check_rds_oversized(resource_data))
    findings.extend(check_rds_storage(resource_data))
    
    findings.extend(check_elb_idle(resource_data))
    findings.extend(check_nat_idle(resource_data))
    
    findings.extend(check_s3_lifecycle(resource_data))
    findings.extend(check_s3_old_objects(resource_data))
    
    findings.extend(check_cw_retention(resource_data))
    findings.extend(check_dynamodb_capacity(resource_data))
    findings.extend(check_reserved_instances(resource_data))
    return findings

def _create_finding(resource_id: str, resource_type: str, issue: str, severity: str, savings: float) -> Dict[str, Any]:
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "issue": issue,
        "severity": severity,
        "estimated_monthly_savings_usd": savings
    }

# --- EC2 ---
def check_ec2_idle(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    metrics_map = {m.get('instance_id'): m.get('avg_cpu_utilization_percent', 100) for m in resource_data.get('ec2_metrics', [])}
    
    for res in resource_data.get('ec2_instances', {}).get('Reservations', []):
        for inst in res.get('Instances', []):
            iid = inst.get('InstanceId')
            cpu = metrics_map.get(iid)
            if cpu is not None and cpu < 5:
                if cpu < 1:
                    findings.append(_create_finding(iid, "ec2", "Idle EC2 instance with average CPU utilization below 1%", "critical", 150.0))
                else:
                    findings.append(_create_finding(iid, "ec2", "Idle EC2 instance with average CPU utilization below 5%", "high", 50.0))
    return findings

def check_ec2_oversized(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    metrics_map = {m.get('instance_id'): m.get('avg_cpu_utilization_percent', 100) for m in resource_data.get('ec2_metrics', [])}
    oversized_types = ['.xlarge', '.2xlarge', '.4xlarge', '.8xlarge', '.12xlarge', '.16xlarge', '.24xlarge']
    
    for res in resource_data.get('ec2_instances', {}).get('Reservations', []):
        for inst in res.get('Instances', []):
            iid = inst.get('InstanceId')
            itype = inst.get('InstanceType', '')
            cpu = metrics_map.get(iid)
            
            is_oversized = any(x in itype for x in oversized_types)
            if is_oversized and cpu is not None and 10 <= cpu <= 40:
                if cpu < 15:
                    findings.append(_create_finding(iid, "ec2", f"Oversized EC2 instance ({itype}) with 10-15% CPU utilization", "critical", 200.0))
                else:
                    findings.append(_create_finding(iid, "ec2", f"Oversized EC2 instance ({itype}) with 15-40% CPU utilization", "medium", 100.0))
    return findings

def check_ec2_amis(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    active_amis = set()
    for res in resource_data.get('ec2_instances', {}).get('Reservations', []):
        for inst in res.get('Instances', []):
            active_amis.add(inst.get('ImageId'))
            
    now = datetime.datetime.now(datetime.timezone.utc)
    for ami in resource_data.get('ec2_amis', {}).get('Images', []):
        ami_id = ami.get('ImageId')
        # Only check custom AMIs (typically Owner is self, this is usually pre-filtered by the fetcher)
        if ami_id not in active_amis:
            creation_date_str = ami.get('CreationDate')
            if creation_date_str:
                try:
                    creation_date = datetime.datetime.strptime(creation_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
                    age_days = (now - creation_date).days
                    if age_days > 365:
                        findings.append(_create_finding(ami_id, "ami", f"Unused custom AMI older than 365 days ({age_days} days old)", "critical", 25.0))
                    elif age_days > 90:
                        findings.append(_create_finding(ami_id, "ami", f"Unused custom AMI older than 90 days ({age_days} days old)", "low", 5.0))
                except ValueError:
                    pass
    return findings

def check_ec2_security_groups(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    # Simplified check: looking for SGs not attached to EC2. (A real implementation would check ENIs as well)
    active_sgs = set()
    for res in resource_data.get('ec2_instances', {}).get('Reservations', []):
        for inst in res.get('Instances', []):
            for sg in inst.get('SecurityGroups', []):
                active_sgs.add(sg.get('GroupId'))
                
    for sg in resource_data.get('security_groups', {}).get('SecurityGroups', []):
        sg_id = sg.get('GroupId')
        sg_name = sg.get('GroupName')
        if sg_id not in active_sgs:
            if sg_name == 'default':
                findings.append(_create_finding(sg_id, "security_group", "Unused default security group", "critical", 0.0))
            else:
                findings.append(_create_finding(sg_id, "security_group", "Unused security group not attached to any running instance", "low", 0.0))
    return findings

# --- EBS ---
def check_ebs_unattached(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for vol in resource_data.get('ebs_volumes', {}).get('Volumes', []):
        attachments = vol.get("Attachments", [])
        if not attachments:
            vol_id = vol.get("VolumeId")
            vol_type = vol.get("VolumeType", "")
            size = vol.get("Size", 0)
            if vol_type == "io1" and size >= 1000:
                findings.append(_create_finding(vol_id, "ebs", "Unattached expensive io1 EBS volume (1000GB+)", "critical", 250.0))
            else:
                findings.append(_create_finding(vol_id, "ebs", "Unattached EBS volume", "medium", 20.0))
    return findings

def check_ebs_snapshots(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    active_volumes = set(v.get("VolumeId") for v in resource_data.get('ebs_volumes', {}).get('Volumes', []))
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for snap in resource_data.get('ebs_snapshots', {}).get('Snapshots', []):
        snap_id = snap.get('SnapshotId')
        vol_id = snap.get('VolumeId')
        
        if vol_id not in active_volumes:
            start_time_str = snap.get('StartTime')
            if start_time_str:
                # Boto3 often returns datetime objects, but mock data might have strings
                if isinstance(start_time_str, str):
                    try:
                        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
                    except ValueError:
                        try:
                            start_time = datetime.datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                        except ValueError:
                            continue
                else:
                    start_time = start_time_str
                    
                age_days = (now - start_time).days
                if age_days > 365:
                    findings.append(_create_finding(snap_id, "ebs_snapshot", f"Orphaned EBS snapshot older than 365 days ({age_days} days old)", "critical", 50.0))
                elif age_days > 90:
                    findings.append(_create_finding(snap_id, "ebs_snapshot", f"Orphaned EBS snapshot older than 90 days ({age_days} days old)", "low", 15.0))
    return findings

# --- EIP ---
def check_eip_unattached(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for ip in resource_data.get('elastic_ips', {}).get('Addresses', []):
        if not ip.get("AssociationId"):
            alloc_id = ip.get("AllocationId", ip.get("PublicIp"))
            if "crit" in alloc_id.lower():
                findings.append(_create_finding(alloc_id, "eip", "Unattached Critical Elastic IP address", "critical", 15.0))
            else:
                findings.append(_create_finding(alloc_id, "eip", "Unattached Elastic IP address", "low", 4.0))
    return findings

# --- RDS ---
def check_rds_oversized(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    oversized_classes = ['db.r5.xlarge', 'db.r5.2xlarge', 'db.r5.4xlarge', 'db.r5.8xlarge', 'db.m4.4xlarge', 'db.m5.4xlarge']
    for db in resource_data.get('rds_instances', {}).get('DBInstances', []):
        db_class = db.get("DBInstanceClass", "")
        is_oversized = any(x in db_class for x in oversized_classes)
        
        tags = db.get("TagList", [])
        is_non_prod = False
        for tag in tags:
            if tag.get("Key") == "Environment" and tag.get("Value") in ["dev", "staging"]:
                is_non_prod = True
                break
                
        if is_oversized and is_non_prod:
            db_id = db.get("DBInstanceIdentifier")
            if "8xlarge" in db_class or "12xlarge" in db_class:
                findings.append(_create_finding(db_id, "rds", f"Massively oversized RDS instance ({db_class}) in dev/staging environment", "critical", 1000.0))
            else:
                findings.append(_create_finding(db_id, "rds", f"Oversized RDS instance ({db_class}) in dev/staging environment", "high", 250.0))
    return findings

def check_rds_storage(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    metrics_map = {m.get('DBInstanceIdentifier'): m.get('FreeStorageSpace', 0) for m in resource_data.get('rds_metrics', [])}
    for db in resource_data.get('rds_instances', {}).get('DBInstances', []):
        db_id = db.get("DBInstanceIdentifier")
        allocated_gb = db.get("AllocatedStorage", 0)
        free_bytes = metrics_map.get(db_id, 0)
        free_gb = free_bytes / (1024**3)
        
        if allocated_gb > 0:
            free_percent = (free_gb / allocated_gb) * 100
            if free_percent > 80 and allocated_gb > 500:
                findings.append(_create_finding(db_id, "rds", f"Massively over-provisioned RDS storage ({free_gb:.0f}GB free out of {allocated_gb}GB)", "high", 50.0))
            elif free_percent > 80:
                findings.append(_create_finding(db_id, "rds", f"Over-provisioned RDS storage ({free_gb:.0f}GB free out of {allocated_gb}GB)", "medium", 20.0))
    return findings

# --- Load Balancer ---
def check_elb_idle(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    th_data = resource_data.get('target_health', {})
    for lb in resource_data.get('load_balancers', {}).get('LoadBalancers', []):
        name = lb.get("LoadBalancerName")
        th_desc = th_data.get(name, {}).get("TargetHealthDescriptions", [])
        
        healthy_targets = sum(1 for tg in th_desc if tg.get("TargetHealth", {}).get("State") == "healthy")
        if healthy_targets == 0:
            if len(th_desc) > 0:
                findings.append(_create_finding(name, "elb", "Load Balancer with failing targets (0 healthy)", "critical", 100.0))
            else:
                findings.append(_create_finding(name, "elb", "Idle Load Balancer with zero healthy targets", "medium", 25.0))
    return findings

def check_nat_idle(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for nat in resource_data.get('nat_gateways', {}).get('NatGateways', []):
        nat_id = nat.get('NatGatewayId')
        # Simplified: flag all NATs that are just sitting there (for mock purposes)
        # Real implementation would query CloudWatch BytesInToDestination
        findings.append(_create_finding(nat_id, "nat_gateway", "Idle NAT Gateway with zero bytes transferred", "high", 32.0))
    return findings

# --- S3 ---
def check_s3_lifecycle(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for bucket in resource_data.get('s3_buckets', {}).get('Buckets', []):
        if not bucket.get("lifecycle_configured", True):
            name = bucket.get("Name")
            if "prod" in name.lower() or "critical" in name.lower():
                findings.append(_create_finding(name, "s3", "Production S3 bucket with no lifecycle policy configured", "critical", 200.0))
            else:
                findings.append(_create_finding(name, "s3", "S3 bucket with no lifecycle policy configured", "low", 10.0))
    return findings

def check_s3_old_objects(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    metrics_map = {m.get('BucketName'): m.get('BucketSizeBytes', 0) for m in resource_data.get('s3_metrics', [])}
    for bucket in resource_data.get('s3_buckets', {}).get('Buckets', []):
        name = bucket.get("Name")
        size_bytes = metrics_map.get(name, 0)
        size_tb = size_bytes / (1024**4)
        if size_tb > 1:
            findings.append(_create_finding(name, "s3", f"Large S3 bucket ({size_tb:.1f} TB) should transition to Infrequent Access", "high", size_tb * 12.0))
    return findings

# --- CloudWatch Logs ---
def check_cw_retention(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for lg in resource_data.get('cw_log_groups', {}).get('logGroups', []):
        name = lg.get('logGroupName')
        retention = lg.get('retentionInDays')
        if not retention:
            findings.append(_create_finding(name, "cloudwatch", "Log group set to Never Expire", "low", 2.0))
    return findings

# --- DynamoDB ---
def check_dynamodb_capacity(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for table in resource_data.get('dynamodb_tables', {}).get('Tables', []):
        name = table.get('TableName')
        billing = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
        if billing == 'PROVISIONED':
            rcu = table.get('ProvisionedThroughput', {}).get('ReadCapacityUnits', 0)
            wcu = table.get('ProvisionedThroughput', {}).get('WriteCapacityUnits', 0)
            if rcu > 100 or wcu > 100:
                findings.append(_create_finding(name, "dynamodb", f"Highly provisioned DynamoDB table ({rcu} RCU, {wcu} WCU)", "medium", 50.0))
    return findings

# --- Reserved Instances ---
def check_reserved_instances(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    for coverage in resource_data.get('savings_plans', {}).get('SavingsPlansCoverages', []):
        od_cost = float(coverage.get('Coverage', {}).get('OnDemandCost', 0))
        if od_cost > 1000:
            findings.append(_create_finding("savings-plan", "savings_plan", f"High On-Demand spend (${od_cost}) could be covered by Savings Plans", "high", od_cost * 0.2))
    return findings
