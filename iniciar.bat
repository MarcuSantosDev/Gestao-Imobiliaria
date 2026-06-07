@echo off
cd /d "%~dp0"

cls

echo ==================================================
echo        CRM - SISTEMA DE GESTAO IMOBILIARIA
echo ==================================================
echo.
echo Acesse o CRM pelo endereco abaixo:
echo.
echo http://127.0.0.1:8000
echo.
echo Aguarde enquanto o servidor e iniciado...
echo.

venv\Scripts\python.exe manage.py runserver

pause