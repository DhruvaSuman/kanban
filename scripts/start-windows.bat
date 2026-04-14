@echo off
set IMAGE_NAME=pm-mvp
set CONTAINER_NAME=pm-mvp-app
set PORT=8000
set ENV_FILE_ARG=
if exist .env set ENV_FILE_ARG=--env-file .env

docker build -t %IMAGE_NAME% .

for /f %%i in ('docker ps -a --format "{{.Names}}" ^| findstr /r "^%CONTAINER_NAME%$"') do (
  docker rm -f %CONTAINER_NAME% >nul
)

docker run -d --name %CONTAINER_NAME% -p %PORT%:8000 %ENV_FILE_ARG% %IMAGE_NAME%
echo Running at http://localhost:%PORT%
