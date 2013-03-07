@echo off
cd /d "%~dp0"
start bin/graph_gen.exe "%~f1"
exit /b
