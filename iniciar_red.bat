@echo off
if "%~1"=="" (
  echo Uso: iniciar_red.bat IP_PC
  exit /b 1
)
call "%~dp0iniciar.bat" --red %*
