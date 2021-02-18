set -e
# Script to test project running in docker container
IMAGE=$1
MODEL_FOLDER=$2
CONTAINER_NAME=translate_server_py_ci_$IMAGE

# start the container
docker run -n $CONTAINER_NAME -p -v ${MODEL_FOLDER}:/root/translate_server_py/mount -itd $IMAGE

# sleep 10 second to wait for service ready
sleep 10

docker exec $CONTAINER_NAME bash -c "PYTHONPATH="./:$PYTHONPATH" python3 test/test_lib_translate.py"
docker exec $CONTAINER_NAME bash -c "PYTHONPATH="./:$PYTHONPATH" python3 test/test_service.py"
