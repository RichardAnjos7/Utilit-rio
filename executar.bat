@echo off
REM Script para executar o Aplicativo Utilitário de Suporte Técnico
REM Verifica se está executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ========================================
    echo   ELEVACAO DE PRIVILEGIOS NECESSARIA
    echo ========================================
    echo.
    echo Este utilitario requer privilegios de administrador.
    echo Solicitando elevacao de privilegios...
    echo.
    REM Solicita elevação e reinicia o script
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM Se chegou aqui, está executando como administrador
echo ========================================
echo   UTILITARIO DE SUPORTE TECNICO
echo   Executando como Administrador
echo ========================================
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



