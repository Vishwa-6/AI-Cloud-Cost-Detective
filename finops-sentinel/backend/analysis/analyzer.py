import json
from .prompts import build_analysis_prompt
from .gemini_client import call_gemini_analysis, GeminiAnalysisError
from .rules_engine import run_all_rules

def _count_total_resources(resource_data: dict) -> int:
    count = 0
    count += sum(len(res.get('Instances', [])) for res in resource_data.get('ec2_instances', {}).get('Reservations', []))
    count += len(resource_data.get('ec2_amis', {}).get('Images', []))
    count += len(resource_data.get('security_groups', {}).get('SecurityGroups', []))
    count += len(resource_data.get('ebs_volumes', {}).get('Volumes', []))
    count += len(resource_data.get('ebs_snapshots', {}).get('Snapshots', []))
    count += len(resource_data.get('elastic_ips', {}).get('Addresses', []))
    count += len(resource_data.get('rds_instances', {}).get('DBInstances', []))
    count += len(resource_data.get('load_balancers', {}).get('LoadBalancers', []))
    count += len(resource_data.get('s3_buckets', {}).get('Buckets', []))
    count += len(resource_data.get('cw_log_groups', {}).get('logGroups', []))
    count += len(resource_data.get('nat_gateways', {}).get('NatGateways', []))
    count += len(resource_data.get('dynamodb_tables', {}).get('Tables', []))
    return count

def analyze_resources(resource_data: dict) -> dict:
    findings = run_all_rules(resource_data)
    
    total_resources = _count_total_resources(resource_data)
    total_savings = sum(f.get("estimated_monthly_savings_usd", 0) for f in findings)
    
    summary = {
        "total_resources_scanned": total_resources,
        "total_issues_found": len(findings),
        "total_estimated_monthly_savings_usd": total_savings
    }
    
    if not findings:
        return {"findings": [], "summary": summary}
        
    try:
        findings_json = json.dumps(findings, indent=2)
    except Exception as e:
        raise GeminiAnalysisError(f"Failed to serialize findings data: {str(e)}")

    full_prompt = build_analysis_prompt(findings_json)
    
    response_dict = call_gemini_analysis(full_prompt)
    
    response_dict["summary"] = summary
    
    enriched_findings = []
    gemini_findings = {f.get("resource_id"): f for f in response_dict.get("findings", [])}
    
    for f in findings:
        rid = f["resource_id"]
        if rid in gemini_findings:
            f["fix_recommendation"] = gemini_findings[rid].get("fix_recommendation", "")
        else:
            f["fix_recommendation"] = "Investigate and resolve this issue."
        enriched_findings.append(f)
        
    response_dict["findings"] = enriched_findings
    
    return response_dict
