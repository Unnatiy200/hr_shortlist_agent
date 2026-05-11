@echo off
color 0A
echo ================================================
echo       HR Resume Shortlisting Agent
echo       Powered by Groq LLaMA 3.3 70B
echo ================================================
echo.
echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit
)
echo.
echo [2/3] Installing required packages...
pip install -r requirements.txt --quiet
echo Packages ready!
echo.
echo [3/3] Starting HR Shortlist Agent...
echo.
echo ================================================
echo  App is opening in your browser...
echo  URL: http://localhost:8501
echo  Press Ctrl+C to stop the app
echo ================================================
echo.
streamlit run app.py
pause