@echo off
REM 自动化管理容器启动

for /f "tokens=*" %%i in ('docker ps -a --filter "name=my_modelscope_app" --format "{{.Names}}"') do (
    echo Container %%i exists. Stopping and removing...
    docker stop %%i
    docker rm %%i
)


echo Building Docker image "my_modelscope_app"...
docker build -t my_modelscope_app .


echo Starting container...
docker run -d -p 5000:5000 --name my_modelscope_app my_modelscope_app

echo.
echo Container "my_modelscope_app" is running.
echo You can access it at http://localhost:5000
pause
