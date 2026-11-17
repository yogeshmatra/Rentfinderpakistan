@echo off
title Rent Finder Pakistan - Web Server
color 0A
echo ======================================================================
echo             RENT FINDER PAKISTAN - WEB SERVER LAUNCHER
echo ======================================================================
echo.
echo Initializing database and verifying records...
python -c "import database; database.init_db(); print('Database ready.')"
echo.
echo Starting Flask application server...
echo Access the website in your browser at: http://127.0.0.1:5000
echo Admin Login: admin@rentfinder.pk ^| Password: admin123
echo.
echo Press Ctrl+C in this terminal window to stop the server anytime.
echo ======================================================================
echo.
python app.py
pause
