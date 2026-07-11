## AI Cloud Cost Detective - Request Flow

① User ─·─·─► React ─·─·─► FastAPI Auth ─·─·─► JWT (SQLite)

② User selects data source (mock / live) ─·─·─► Python Backend

③ Python ─·─·─► boto3 ─·─·─► Fetches 12 resource types from mock JSON or live AWS

④ Python ─·─·─► FastAPI WebSocket ─·─·─► React (live progress updates)

⑤ Python ─·─·─► Rules Engine ─·─·─► Runs 16 deterministic checks (Critical, High, Medium, Low)

⑥ Python ─·─·─► Gemini API ─·─·─► Generates fix recommendations for findings

⑦ Python ─·─·─► SQLite ─·─·─► Stores analysis history

⑧ React ◄·─·─·─ Final report with Donut Chart, Findings Table & CSV Export