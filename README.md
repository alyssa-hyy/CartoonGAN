构建镜像
`docker build -t my_backend .`
自动化管理写一个批处理脚本（.bat 文件）管理容器启动

**使用 CPU 模式运行**
使用了 --rm 参数，容器在退出后就会自动删除
`docker run -it --rm -p 5000:5000 my_modelscope_app`

**使用 GPU 模式运行**
`docker run --gpus all -it --rm -p 5000:5000 my_modelscope_app`


**查看正在运行的容器**
`docker ps`
**使用以下命令可以查看容器的标准输出和错误日志**
docker logs <容器ID或容器名称>

**在容器内使用curl命令测试接口**
1.进入容器内部
`docker exec -it <容器ID或容器名称> bash`
2.发送测试请求
`curl -X POST http://localhost:5000/process -F "file=@/path/to/test.jpg"`

退出容器
`ctrl + D`
停止正在运行的容器
`docker stop <容器ID或容器名称>`
