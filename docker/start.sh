# 自动生成docker-compose.yaml, nginx.conf并启动所有容器
FOLDER=$1  # 存放模型的工作目录
IMAGE_TAG=$2  # docker image tag
PORT=$3  # nginx serve port

python generate_docker_compose_yaml.py ${FOLDER} ${IMAGE_TAG} ${PORT}
python generate_nginx_conf.py ${FOLDER}

cd ${FOLDER}
docker-compose up -d

