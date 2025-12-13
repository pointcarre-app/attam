# FastAPI app with uvicorn
web: PYTHONPATH=/app uvicorn backend.main:app --workers 2 --timeout-keep-alive 60 --host 0.0.0.0 --port $PORT --proxy-headers