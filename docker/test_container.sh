set -e
# Script to test project running in docker container
IMAGE=$1
MODEL_FOLDER=$2
CONTAINER_NAME=translate_server_py_ci_$IMAGE
if [[ $IMAGE =~ "device_cuda" ]]
then
  RUNTIME_FLAG="--runtime=nvidia"
fi

# start the container
docker run -n $CONTAINER_NAME $RUNTIME_FLAG -p -v ${MODEL_FOLDER}:/root/translate_server_py/mount -itd $IMAGE

# sleep 10 second to wait for service ready
sleep 10

docker exec $CONTAINER_NAME bash -c "PYTHONPATH="./:$PYTHONPATH" python3 test/test_lib_translate.py"
docker exec $CONTAINER_NAME bash -c "PYTHONPATH="./:$PYTHONPATH" python3 test/test_service.py"
