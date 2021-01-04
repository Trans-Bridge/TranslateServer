# 自动生成docker-compose.yaml, nginx.conf并启动所有容器
FOLDER=$1  # 存放模型的工作目录
IMAGE_VERSION=$2  # docker image tag
PORT=$3  # nginx serve port

SOURCE_ROOT=$(pwd)

# prapare
python docker/generate_docker_file.py ${FOLDER} --folder ${FOLDER} --version ${IMAGE_VERSION} --build
python docker/generate_docker_compose_yaml.py ${FOLDER} ${IMAGE_VERSION} ${PORT}
python docker/generate_nginx_conf.py ${FOLDER}

# start all containers
cd ${FOLDER}
docker-compose up -d
echo "Waiting for containers ready."
sleep 10s

# test for deployment
cd ${SOURCE_ROOT}
export PYTHONPATH="${PYTHONPATH}:${SOURCE_ROOT}"
python test/test_deployment.py ${FOLDER} --port ${PORT}
