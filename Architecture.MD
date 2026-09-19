## AI Cloud Cost Detective - Architecture

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
                                         └───┬───────┬───┬───┘
                                             :       :   :
                              ┌──────────────┘       :   └──────────────┐
                              :                      :                  :
                              ▼                      ▼                  ▼
                         ┌─────────────┐     ┌──────────────┐    ┌──────────────┐
                         │ AWS FETCHER │     │   FASTAPI    │    │ DETERMINISTIC│
                         │ (Mock/Live) │     │  WEBSOCKET   │    │ RULES ENGINE │
                         └──────┬──────┘     └──────┬───────┘    └──────┬───────┘
                                :                   :                   :
                                ▼                   ▼                   ▼
                        ┌─────────────┐     ┌──────────────┐    ┌──────────────┐
                        │ 12 AWS      │     │   REACT      │    │  GEMINI AI   │
                        │ RESOURCE    │     │  (Progress   │    │ (Remediation │
                        │  TYPES      │     │   Tracker)   │    │  Only)       │
                        └─────────────┘     └──────────────┘    └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │    SQLITE    │
                                           │  (Database)  │
                                           └──────┬───────┘
                                                  :
                                                  ▼
                                           ┌───────────────┐
                                           │    REACT      │
                                           │ (Final Report │
                                           │   Dashboard)  │
                                           └───────────────┘
