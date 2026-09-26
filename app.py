"""
Convenience entry point for the backend.

You can run the backend either way:
    uvicorn backend.api:app --reload      (recommended, has auto-reload)
    python app.py                          (also works, no auto-reload)

The Streamlit frontend is always run separately:
    streamlit run frontend/dashboard.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=False)
