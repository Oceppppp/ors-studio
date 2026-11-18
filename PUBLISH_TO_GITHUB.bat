@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "REPO=Oceppppp/ors-studio"
set "EXPECTED_USER=Oceppppp"
set "VERSION=0.4.0"
set "TAG=v0.4.0"
set "DESCRIPTION=ORS Studio - public Web and Desktop Operations Research platform with 29 solver modules"

echo.
echo ============================================================
echo   ORS Studio v%VERSION% - Publish public repository
echo ============================================================
echo.

echo This script publishes source code to the PUBLIC repository:
echo https://github.com/%REPO%
echo It will not publish local .env files or SQLite databases.
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Git for Windows is not installed.
  echo Install from https://git-scm.com/download/win and run again.
  pause
  exit /b 1
)

where gh >nul 2>&1
if errorlevel 1 (
  echo [INFO] GitHub CLI is not installed.
  where winget >nul 2>&1
  if errorlevel 1 (
    echo Install GitHub CLI from https://cli.github.com/ and run again.
    pause
    exit /b 1
  )
  choice /C YN /M "Install GitHub CLI now using Windows Package Manager"
  if errorlevel 2 exit /b 1
  winget install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo [ERROR] GitHub CLI installation failed.
    pause
    exit /b 1
  )
  echo [INFO] GitHub CLI installed. Close this window, reopen it, then run this script again.
  pause
  exit /b 0
)

 gh auth status --hostname github.com >nul 2>&1
if errorlevel 1 (
  echo [INFO] A browser will open for GitHub authentication.
  gh auth login --hostname github.com --git-protocol https --web
  if errorlevel 1 goto :auth_error
)

for /f "delims=" %%U in ('gh api user --jq .login 2^>nul') do set "AUTH_USER=%%U"
if /I not "%AUTH_USER%"=="%EXPECTED_USER%" (
  echo [ERROR] Signed-in account is "%AUTH_USER%", expected "%EXPECTED_USER%".
  echo Run: gh auth logout --hostname github.com
  echo Then rerun this script and sign in as %EXPECTED_USER%.
  pause
  exit /b 1
)
echo [OK] GitHub account: %AUTH_USER%

echo.
echo [INFO] Requesting repository and workflow permissions for source publishing and GitHub Actions.
gh auth refresh --hostname github.com --scopes repo,workflow
if errorlevel 1 (
  echo [ERROR] Could not obtain repo/workflow scopes. Re-run gh auth refresh interactively.
  pause
  exit /b 1
)

REM Block common local secrets/data before staging files.
if exist ".env" (
  echo [ERROR] .env exists in this folder. Remove it or move it outside the project before publishing.
  pause
  exit /b 1
)
if exist "ors.sqlite3" (
  echo [ERROR] Local database ors.sqlite3 exists. Move it outside the project before publishing.
  pause
  exit /b 1
)
if exist "ors-web-dev.sqlite3" (
  echo [ERROR] Local database ors-web-dev.sqlite3 exists. Move it outside the project before publishing.
  pause
  exit /b 1
)
if exist ".venv" echo [WARNING] .venv exists; it is ignored by Git but may be deleted for a cleaner source tree.

REM Refuse to publish if likely credentials were placed in tracked env-like files.
for %%F in (.env .env.production .env.local) do if exist "%%F" (
  echo [ERROR] Found secret configuration file %%F. Remove it before publishing.
  pause
  exit /b 1
)

REM Initialize local git safely; never force-push.
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  git init -b main
  if errorlevel 1 goto :git_error
) else (
  git branch -M main
  if errorlevel 1 goto :git_error
)

for /f "delims=" %%N in ('git config user.name 2^>nul') do set "GIT_NAME=%%N"
if not defined GIT_NAME git config --local user.name "ORS Studio Publisher"
for /f "delims=" %%E in ('git config user.email 2^>nul') do set "GIT_EMAIL=%%E"
if not defined GIT_EMAIL git config --local user.email "ors-studio-publisher@users.noreply.github.com"

git add -A
if errorlevel 1 goto :git_error

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Publish ORS Studio v%VERSION%: public Web and Desktop editions"
  if errorlevel 1 goto :git_error
)

REM Verify or create the intended PUBLIC repository.
gh repo view "%REPO%" --json visibility --jq .visibility >nul 2>&1
if errorlevel 1 (
  echo [INFO] Creating new PUBLIC repository %REPO% and pushing source...
  gh repo create "%REPO%" --public --description "%DESCRIPTION%" --source . --remote origin --push
  if errorlevel 1 goto :publish_error
) else (
  set "VISIBILITY="
  for /f "delims=" %%V in ('gh repo view "%REPO%" --json visibility --jq .visibility 2^>nul') do set "VISIBILITY=%%V"
  if /I not "!VISIBILITY!"=="PUBLIC" (
    echo [ERROR] Target repository exists but is not PUBLIC. No visibility change was made.
    pause
    exit /b 1
  )
  git remote get-url origin >nul 2>&1
  if errorlevel 1 (
    git remote add origin "https://github.com/%REPO%.git"
    if errorlevel 1 goto :git_error
  ) else (
    set "ORIGIN_URL="
    for /f "delims=" %%R in ('git remote get-url origin') do set "ORIGIN_URL=%%R"
    echo !ORIGIN_URL! | findstr /I /C:"%REPO%" >nul
    if errorlevel 1 (
      echo [ERROR] Existing origin points to a different repository: !ORIGIN_URL!
      echo No changes were pushed. Review the remote manually.
      pause
      exit /b 1
    )
  )
  git push -u origin main
  if errorlevel 1 goto :publish_error
)

REM Create/push a release tag, but never overwrite an existing tag.
git show-ref --tags --verify --quiet "refs/tags/%TAG%"
if errorlevel 1 (
  git tag -a "%TAG%" -m "ORS Studio %VERSION%"
  if errorlevel 1 goto :git_error
) else (
  for /f "delims=" %%S in ('git rev-list -n 1 "%TAG%"') do set "TAG_SHA=%%S"
  for /f "delims=" %%S in ('git rev-parse HEAD') do set "HEAD_SHA=%%S"
  if /I not "!TAG_SHA!"=="!HEAD_SHA!" (
    echo [ERROR] Local tag %TAG% already points to a different commit. It was not changed.
    pause
    exit /b 1
  )
)
git push origin "%TAG%"
if errorlevel 1 goto :publish_error

echo.
echo [SUCCESS] Source and tag %TAG% pushed to https://github.com/%REPO%
echo [NEXT] GitHub Actions will run the Web test and Windows Desktop release workflows.
echo [NEXT] Connect the repository to Render and apply render.yaml to provision the public Web edition.
echo [NOTE] This script does not provision Render services or configure a custom domain.
echo.
pause
exit /b 0

:auth_error
echo [ERROR] GitHub login did not complete.
pause
exit /b 1

:git_error
echo [ERROR] A Git operation failed. Review the output above; no force push was attempted.
pause
exit /b 1

:publish_error
echo [ERROR] GitHub repository creation or push failed. No force push was attempted.
echo Check GitHub CLI permissions, repository visibility, and unrelated remote commits.
pause
exit /b 1
