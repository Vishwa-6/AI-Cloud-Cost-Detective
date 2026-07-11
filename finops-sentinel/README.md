# 🛡️ FinOps Sentinel

**FinOps Sentinel** is an advanced, open-source AWS cost analysis agent. It uses a **hybrid architecture**: a robust Python-based deterministic rules engine to flag cloud waste with 100% accuracy across 4 severity tiers (Critical, High, Medium, Low), paired with Google's Gemini AI to generate actionable, human-readable remediation steps.

---

## ✨ Features

- **16 Deterministic Detection Rules** across 12 AWS resource types
- **4 Severity Tiers**: Critical, High, Medium, Low
- **Hybrid AI Architecture**: Python detects issues → Gemini writes fix recommendations
- **Real-Time WebSocket Progress**: Watch the scan happen live in your browser
- **Scan History**: All past scans saved to SQLite, viewable anytime
- **Interactive Dashboard**: Donut chart, severity filters, sortable table, expandable fix recommendations
- **CSV Export**: One-click download of all findings
- **4-Model Gemini Fallback Chain**: Automatic failover if a model is rate-limited
- **Dual Data Sources**: Mock mode (offline testing) and Live mode (real AWS via boto3)
- **JWT Authentication** with bcrypt password hashing and rate limiting

## 🔍 What It Detects

| Resource Type | Rule | Severity |
|---|---|---|
| EC2 Instances | Idle instances (CPU < 5%, < 1%) | High / Critical |
| EC2 Instances | Oversized instances (xlarge+ at 10-40% CPU) | Medium / Critical |
| EC2 AMIs | Unused custom AMIs (> 90 days, > 365 days) | Low / Critical |
| Security Groups | Unused security groups, unused defaults | Low / Critical |
| EBS Volumes | Unattached volumes, expensive io1 volumes | Medium / Critical |
| EBS Snapshots | Orphaned snapshots (> 90 days, > 365 days) | Low / Critical |
| Elastic IPs | Unassociated Elastic IPs | Low / Critical |
| RDS Instances | Oversized in dev/staging (xlarge, 8xlarge) | High / Critical |
| RDS Storage | Over-provisioned storage (> 80% free) | Medium / High |
| Load Balancers | Zero healthy targets, all targets failing | Medium / Critical |
| NAT Gateways | Idle gateways with zero traffic | High |
| S3 Buckets | No lifecycle policy (prod buckets → critical) | Low / Critical |
| S3 Buckets | Large buckets (> 1TB) for IA transition | High |
| CloudWatch Logs | Log groups set to Never Expire | Low |
| DynamoDB | Over-provisioned capacity (> 100 RCU/WCU) | Medium |
| Savings Plans | High On-Demand spend without coverage | High |

---

## 🔒 Security First: The IAM Policy Strategy

As an open-source tool, we believe in the **Principle of Least Privilege**. You should **never** provide root AWS credentials or full Admin access to any third-party tool. 

FinOps Sentinel is designed as a "Cost Detective"—it only needs to *look* at your resources, not touch them. Because of this, it requires **strictly Read-Only access**.

### Why do we recommend a custom policy?
1. **Zero Risk:** If your API keys are ever compromised, attackers cannot spin up crypto miners, delete your databases, or alter your infrastructure.
2. **Transparency:** You know exactly what data this tool is looking at. 
3. **Peace of Mind:** The tool cannot accidentally terminate production EC2 instances.

### 📝 The Custom "FinOps Sentinel" IAM Policy
Before running the app, create a new IAM User in your AWS console and attach this exact JSON policy. It explicitly limits access to only the `Describe`, `List`, and `Get` actions required by the rules engine.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "FinOpsSentinelReadOnly",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "ec2:DescribeAddresses",
                "ec2:DescribeImages",
                "ec2:DescribeSnapshots",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeNatGateways",
                "rds:DescribeDBInstances",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetHealth",
                "s3:ListAllMyBuckets",
                "s3:GetBucketLifecycleConfiguration",
                "cloudwatch:GetMetricStatistics",
                "logs:DescribeLogGroups",
                "dynamodb:ListTables",
                "dynamodb:DescribeTable",
                "ce:GetSavingsPlansCoverage"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 📂 Project Structure

```
finops-sentinel/
├── backend/
│   ├── main.py                    # FastAPI entrypoint
│   ├── limiter.py                 # Rate limiting config
│   ├── requirements.txt           # Python dependencies
│   ├── analysis/
│   │   ├── rules_engine.py        # 16 deterministic check functions
│   │   ├── analyzer.py            # Orchestrates rules → Gemini enrichment
│   │   ├── gemini_client.py       # 4-model fallback chain
│   │   └── prompts.py             # Gemini prompt template
│   ├── auth/
│   │   ├── routes.py              # Signup, login, /me endpoints
│   │   ├── security.py            # JWT + bcrypt
│   │   ├── models.py              # User model
│   │   ├── schemas.py             # Pydantic schemas
│   │   └── database.py            # SQLAlchemy + SQLite
│   ├── aws_fetcher/
│   │   ├── base.py                # Abstract base class (17 methods)
│   │   ├── mock_source.py         # Reads from mock_data/ JSON files
│   │   ├── live_source.py         # Real boto3 AWS API calls
│   │   └── fetcher.py             # Factory: mock vs live
│   └── scan/
│       ├── routes.py              # WebSocket + REST scan endpoints
│       ├── orchestrator.py        # Fetch → Analyze → Save → Complete
│       └── models.py              # Analysis DB model
├── frontend/
│   └── src/
│       ├── App.tsx                # Main app with routing
│       ├── components/
│       │   ├── FindingsDashboard  # Table with filters, sort, CSV export
│       │   ├── FindingsChart      # SVG donut chart
│       │   ├── ScanTrigger        # Mode selector + scan button
│       │   ├── ScanProgress       # Real-time step tracker
│       │   └── ProtectedRoute     # Auth guard
│       ├── hooks/
│       │   └── useScanWebSocket   # WebSocket lifecycle hook
│       ├── pages/
│       │   ├── LoginPage
│       │   ├── SignupPage
│       │   └── HistoryPage        # Past scan viewer
│       └── context/
│           └── AuthContext         # JWT token management
├── mock_data/                     # 17 JSON files for offline testing
└── tests/
    └── test_rules_engine.py       # Deterministic pytest suite
```

---

## 🚀 Getting Started

### 1. Configure AWS Credentials (for Live Mode only)
You do not need to hardcode your AWS keys into the app. FinOps Sentinel uses `boto3`, which automatically detects your local AWS profiles.
Run the AWS CLI configure command and paste the Access Keys of the Read-Only IAM User you created above:
```bash
aws configure
```

> **Note:** You can skip this step and use Mock Mode to test the tool without any AWS account.

### 2. Configure Environment Variables
Clone the repository, navigate to the project root, and set up your `.env` file. You will need a free Google Gemini API key.
```bash
cp .env.example .env
```
Inside `.env`, add:
```
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_random_secret_here
```

### 3. Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173`, create a local account, and click **Run Scan**! Select **Mock Mode** to test immediately without AWS credentials, or **Live Mode** to scan your real AWS infrastructure.

### 5. Running with Docker Compose (Alternative)
You can run the entire application (Frontend, Backend, and Nginx reverse proxy) in one go using Docker Compose. Ensure you have populated `.env` in the root directory, then run:

```bash
docker-compose up --build
```

- The **Frontend** will be accessible at: `http://localhost:3000`
- The **Backend** API will be running at: `http://localhost:8000`

Docker Compose automatically mounts a named volume `backend-data` for the SQLite database so your users and scan history persist between container restarts.

---

## 🧪 Running Tests

```bash
# From the project root (no API keys needed)
python -m pytest tests/test_rules_engine.py -v
```

This runs the deterministic rules engine test suite against all 17 mock data files, asserting that exactly 26 findings are produced with the correct severities, and that healthy resources are never falsely flagged.

---

## 📄 License

Open-source. See LICENSE file for details.
