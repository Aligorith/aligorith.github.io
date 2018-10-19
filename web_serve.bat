@echo off
echo Running Python server for %cd%
start firefox http://localhost:8000
python3 -m http.server
