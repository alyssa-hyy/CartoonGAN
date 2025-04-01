FROM modelscope-registry.cn-beijing.cr.aliyuncs.com/modelscope-repo/modelscope:ubuntu22.04-cuda12.1.0-py311-torch2.3.1-tf2.16.1-1.24.0

# 更新系统库，尝试安装较新版本的 libstdc++6
RUN apt-get update && apt-get install -y libstdc++6

# 设置工作目录
WORKDIR /app

# 复制并安装项目依赖（确保 requirements.txt 包含 Flask 以及其它你需要的包）
COPY requirements /app/
RUN pip install --no-cache-dir -r requirements

# 复制项目代码到容器中
COPY . /app

EXPOSE 5000

# 默认启动 app.py
CMD ["python", "app.py"]
