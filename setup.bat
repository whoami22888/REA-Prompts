@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Install checked-in REAP skills; regeneration is an explicit developer step.
set "ROOT=%~dp0"
set "AGENT=%~1"
if "%AGENT%"=="" set "AGENT=all"
if not "%~2"=="" goto usage
if /I "%AGENT%"=="hermes" goto hermes
if /I "%AGENT%"=="claude" goto claude
if /I "%AGENT%"=="claude-code" goto claude
if /I "%AGENT%"=="codex" goto codex
if /I "%AGENT%"=="all" goto all
:usage
echo usage: setup.bat [hermes^|claude-code^|codex^|all] 1>&2
exit /b 2
:hermes
call :install "%USERPROFILE%\.hermes\skills" || exit /b 1
goto done
:claude
call :install "%USERPROFILE%\.claude\skills" || exit /b 1
goto done
:codex
call :install "%USERPROFILE%\.codex\skills" || exit /b 1
goto done
:all
set "FOUND=0"
if exist "%USERPROFILE%\.hermes" (
  call :install "%USERPROFILE%\.hermes\skills"
  if errorlevel 1 exit /b 1
)
if exist "%USERPROFILE%\.hermes" set "FOUND=1"
if exist "%USERPROFILE%\.claude" (
  call :install "%USERPROFILE%\.claude\skills"
  if errorlevel 1 exit /b 1
)
if exist "%USERPROFILE%\.claude" set "FOUND=1"
if exist "%USERPROFILE%\.codex" (
  call :install "%USERPROFILE%\.codex\skills"
  if errorlevel 1 exit /b 1
)
if exist "%USERPROFILE%\.codex" set "FOUND=1"
if "%FOUND%"=="0" (
  echo No supported agent directory found. Specify hermes, claude-code or codex to create one. 1>&2
  exit /b 1
)
goto done
:install
set "DEST=%~1"
if not exist "%DEST%" mkdir "%DEST%" || exit /b 1
set /a COUNT=0
for /d %%S in ("%ROOT%Skills\reap-*") do (
  if exist "%%~fS\SKILL.md" (
    xcopy /E /I /Q /Y "%%~fS" "%DEST%\%%~nxS" >nul
    if errorlevel 1 exit /b 1
    set /a COUNT+=1
  )
)
if not "%COUNT%"=="26" (
  echo Expected 26 REAP skills, installed %COUNT% 1>&2
  exit /b 1
)
echo installed %COUNT% skill packs -^> "%DEST%"
exit /b 0
:done
echo.
echo REAP installed. Reload your agent session to discover the skills.
echo Full-library system prompt: "%ROOT%system_prompt.md"
exit /b 0