@echo off
REM Script para executar o Aplicativo Utilitário de Suporte Técnico
echo Iniciando Utilitario de Suporte Tecnico...
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.7 ou superior.
    pause
    exit /b 1
)

REM Executa o aplicativo
python main.py

if errorlevel 1 (
    echo.
    echo Erro ao executar o aplicativo.
    pause
)



