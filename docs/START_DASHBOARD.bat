@echo off
echo ============================================
echo    POKER DASHBOARD HTTP SERVER
echo ============================================
echo.
echo Starting HTTP server for poker dashboard...
echo Dashboard will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python -m http.server 8000

pause