## AI Cloud Cost Detective - Architecture

```
                   
                     ┌──────────────┐
                     │     USER     │
                     └──────┬───────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │  REACT FRONTEND   │
                  └────────┬──────────┘
                           :
                           : Login / Signup
                           ▼
                  ┌───────────────────┐
                  │  PYTHON BACKEND   │
                  │    (FastAPI)      │
                  │                   │
                  │  · Custom JWT Auth│
                  └───┬───────┬───┬───┘
                      :       :   :
       ┌──────────────┘       :   └──────────────┐
       :                      :                  :
       ▼                      ▼                  ▼
┌─────────────┐     ┌──────────────┐    ┌──────────────┐
│   BOTO3     │     │   FASTAPI    │    │   GEMINI     │
│             │     │  WEBSOCKET   │    │    API       │
│ Mock JSON / │     │  (Progress)  │    │              │
│ Live AWS API│     └──────┬───────┘    │ Cost Analysis│
└──────┬──────┘            :            └──────┬───────┘
       :                   : Live updates      :
       ▼                   ▼                   :
┌─────────────┐   ┌───────────────┐            :
│  MOCK DATA  │   │    REACT      │            :
│  or AWS     │   │  (Progress    │            :
│ (EC2/RDS/S3)│   │   Tracker)    │            :
└─────────────┘   └───────────────┘            :
                                               ▼
                                        ┌──────────────┐
                                        │  POSTGRESQL  │
                                        │  (SQLite/    │
                                        │   Docker)    │
                                        │              │
                                        │ · users      │
                                        │ · analyses   │
                                        └──────┬───────┘
                                               :
                                               : Stored results
                                               ▼
                                        ┌───────────────┐
                                        │    REACT      │
                                        │ (Final Report │
                                        │  + Suggestions│
                                        │  + Fixes)     │
                                        └───────────────┘
                                        
```