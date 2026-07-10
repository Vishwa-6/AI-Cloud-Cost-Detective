## AI Cloud Cost Detective - Request Flow

```

User ─·─·─► React ─·─·─► FastAPI Auth ─·─·─► JWT (PostgreSQL/SQLite)

②  User selects data source (mock / live) + AWS region or mock set ─·─·─► Python Backend

③  Python ─·─·─► boto3 ─·─·─► Fetches all resources (EC2, RDS, S3, ELB) from mock JSON or live AWS

④  Python ─·─·─► FastAPI WebSocket ─·─·─► React (live progress)

⑤  Python ─·─·─► Gemini API ─·─·─► Cost analysis (structured JSON output)

⑥  Python ─·─·─► PostgreSQL/SQLite ─·─·─► Stores analysis history

⑦  React ◄·─·─·─ Final report with suggestions & fixes

```