@echo off
set CONTAINER_NAME=pm-mvp-app

for /f %%i in ('docker ps -a --format "{{.Names}}" ^| findstr /r "^%CONTAINER_NAME%$"') do (
  docker rm -f %CONTAINER_NAME%
  echo Stopped %CONTAINER_NAME%
  goto :eof
)

echo No running container named %CONTAINER_NAME%
