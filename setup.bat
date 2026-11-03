@echo off
setlocal EnableExtensions EnableDelayedExpansion
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
set "TARGETS="
if /i "%AGENT%"=="hermes" set "TARGETS=%USERPROFILE%\.hermes\skills"
if /i "%AGENT%"=="claude-code" set "TARGETS=%USERPROFILE%\.claude\skills"
if /i "%AGENT%"=="claude" set "TARGETS=%USERPROFILE%\.claude\skills"
if /i "%AGENT%"=="codex" set "TARGETS=%USERPROFILE%\.codex\skills"
if /i "%AGENT%"=="all" (
  if exist "%USERPROFILE%\.hermes" set "TARGETS=!TARGETS!;"%USERPROFILE%\.hermes\skills""
  if exist "%USERPROFILE%\.claude" set "TARGETS=!TARGETS!;"%USERPROFILE%\.claude\skills""
  if exist "%USERPROFILE%\.codex" set "TARGETS=!TARGETS!;"%USERPROFILE%\.codex\skills""
)
if not defined TARGETS (
  echo ERROR: No matching agent directory found, or unsupported agent. 1>&2
  exit /b 1
)

set /a COUNT=0
for %%D in (!TARGETS:;= !) do (
  if not exist "%%~D" mkdir "%%~D"
  if errorlevel 1 exit /b 1
  for /d %%S in ("Skills\reap-*") do (
    if not exist "%%~D\%%~nxS" mkdir "%%~D\%%~nxS"
    xcopy /e /i /q /y "%%~fS\*" "%%~D\%%~nxS\" >nul
    if errorlevel 1 exit /b 1
    set /a COUNT+=1
  )
  echo Installed REAP packs into %%~D
)
echo Install complete. Reload your agent session.
exit /b 0
