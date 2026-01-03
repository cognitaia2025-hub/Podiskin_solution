@echo off
cd /d C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution\backend
call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
