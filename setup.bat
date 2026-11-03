@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where python >nul 2>&1
if not errorlevel 1 (
  set "PYTHON=python"
) else (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Python 3 is required. 1>&2
    exit /b 1
  )
  set "PYTHON=py -3"
)

%PYTHON% tools\build_skills.py
if errorlevel 1 exit /b 1
%PYTHON% tools\build_system_prompt.py
if errorlevel 1 exit /b 1

set "AGENT=%~1"
if "%AGENT%"=="" set "AGENT=all"

if /i "%AGENT%"=="hermes" (
  call :install "%USERPROFILE%\.hermes\skills"
  exit /b %errorlevel%
)
if /i "%AGENT%"=="claude-code" (
  call :install "%USERPROFILE%\.claude\skills"
  exit /b %errorlevel%
)
if /i "%AGENT%"=="claude" (
  call :install "%USERPROFILE%\.claude\skills"
  exit /b %errorlevel%
)
if /i "%AGENT%"=="codex" (
  call :install "%USERPROFILE%\.codex\skills"
  exit /b %errorlevel%
)
if /i not "%AGENT%"=="all" (
  echo ERROR: Invalid agent "%AGENT%". 1>&2
  exit /b 2
)

set "FOUND="
if exist "%USERPROFILE%\.hermes" (
  call :install "%USERPROFILE%\.hermes\skills"
  if errorlevel 1 exit /b 1
  set "FOUND=1"
)
if exist "%USERPROFILE%\.claude" (
  call :install "%USERPROFILE%\.claude\skills"
  if errorlevel 1 exit /b 1
  set "FOUND=1"
)
if exist "%USERPROFILE%\.codex" (
  call :install "%USERPROFILE%\.codex\skills"
  if errorlevel 1 exit /b 1
  set "FOUND=1"
)
if not defined FOUND (
  echo ERROR: No supported agent directory detected. 1>&2
  exit /b 1
)
echo Install complete. Reload your agent session.
exit /b 0

:install
set "TARGET=%~1"
if not exist "%TARGET%" mkdir "%TARGET%"
if errorlevel 1 exit /b 1
set /a COUNT=0
for /d %%S in ("Skills\reap-*") do (
  if not exist "%TARGET%\%%~nxS" mkdir "%TARGET%\%%~nxS"
  if errorlevel 1 exit /b 1
  xcopy /e /i /q /y "%%~fS\*" "%TARGET%\%%~nxS\" >nul
  if errorlevel 1 exit /b 1
  set /a COUNT+=1
)
if not exist "%TARGET%\reap-prompts\SKILL.md" exit /b 1
echo Installed REAP skills to "%TARGET%"
exit /b 0
