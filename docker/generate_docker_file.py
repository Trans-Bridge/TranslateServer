"""
自动生成dockerfile
"""
import argparse
import subprocess
import os
import yaml

SOURCE_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
IMAGE_NAME = "translate_server_py"

CUDA_BASE = r"""
ARG PYTORCH_VERSION=1.7.0-cuda11.0-cudnn8-runtime
FROM pytorch/pytorch:${PYTORCH_VERSION}

# install neccesary packcages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        git \
        g++ \
        make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

"""

CPU_BASE = r"""
ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

"""


GENERAL = r"""
# update pip
RUN pip install -i https://pypi.douban.com/simple --upgrade pip

WORKDIR /root
ENV CMAKE_VERSION=3.18.4
# This is a mirror of https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/cmake-$CMAKE_VERSION-Linux-x86_64.tar.gz
RUN wget -q https://gitee.com/brightxiaohan/CMake/attach_files/615214/download/cmake-$CMAKE_VERSION-Linux-x86_64.tar.gz && \
    tar xf *.tar.gz && \
    rm *.tar.gz
ENV PATH=$PATH:/root/cmake-$CMAKE_VERSION-Linux-x86_64/bin

# manually install pyltp
RUN git clone https://github.com/HIT-SCIR/pyltp.git && \
    cd pyltp && \
    git checkout v0.4.0 && \
    git submodule init && \
    git submodule update && \
    python setup.py install && \
    cd .. && \
    rm -rf pyltp

# manually install faiseq (use the version which we train model on)
# fairseq commit id 265791b727b664d4d7da3abd918a3f6fb70d7337
# fairseq tag v0.10.1
RUN git clone https://github.com/pytorch/fairseq.git && \
    cd fairseq && \
    git checkout {fairseq_version} && \  
    pip install -i https://pypi.douban.com/simple . && \
    cd .. && \
    rm -rf fairseq

COPY requirements.txt requirements.txt
COPY scripts/download_nltk_model.py download_nltk_model.py
RUN pip install -i https://pypi.douban.com/simple -r requirements.txt && \
    python download_nltk_model.py && \
    rm requirements.txt download_nltk_model.py

ARG SOURCEDIR=/root/translate_server_py/
WORKDIR ${{SOURCEDIR}}
ADD . ${{SOURCEDIR}}

EXPOSE 80
CMD [ "python", "service.py" ]

"""


def parse_args():
    """
    解析脚本参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", type=str, help="输出dockerfile的目录")
    parser.add_argument("--version", type=str, default="latest", help="构建镜像的版本")
    parser.add_argument("--device", type=str, default=None,
                        choices=['cuda', 'cpu'], help="模型运行设备类型，支持cpu和cuda")
    parser.add_argument("--fairseq_version", type=str, default=None,
                        help="fairseq模型训练版本，防止不同版本质检模型兼容性问题")
    parser.add_argument("--folder",
                        type=str,
                        default=None,
                        help="存放模型的路径，此参数可根据所有子目录的配置信息生成不同的dockerfile，在前面两个参数为空时生效")
    parser.add_argument("--build", action="store_true",
                        default=False, help="是否构建镜像")
    args = parser.parse_args()
    return args


def generate_dockerfile(output_path, device, fairseq_version):
    """
    根据参数生成dockerfile
    """
    head = CUDA_BASE if device == "cuda" else CPU_BASE
    body = GENERAL.format(fairseq_version=fairseq_version)

    dockerfile_string = head + body
    with open(output_path, "w") as output_file:
        output_file.write(dockerfile_string)


def parse_all_tags(folder):
    """
    根据目录中所有待部署模型的配置文件中解析dockerfile生成参数
    """
    names = (name for name in next(os.walk(folder))[1])
    all_tags = set()
    for name in names:
        subdir = os.path.join(folder, name)
        config_file = os.path.join(subdir, "config.yaml")
        if not os.path.isfile(config_file):
            continue

        # 读取配置文件中与docker相关的配置
        with open(config_file) as cfg_f:
            config = yaml.load(cfg_f.read())

        docker_image_tag_suffix = config.get(
            "docker_image_tag_suffix", "device_cpu-fairseq_v0.10.1")
        device, fairseq_version = docker_image_tag_suffix.split("-")
        device = device.split("_")[1]
        fairseq_version = fairseq_version.split("_")[1]

        all_tags.add((docker_image_tag_suffix, device, fairseq_version))
    return list(all_tags)


def build_image(dockerfile, name, tag):
    """
    使用docker命令构建镜像
    """
    cmd = "docker build -t {name}:{tag} -f {dockerfile} {source_root_dir}".format(
        name=name,
        tag=tag,
        dockerfile=dockerfile,
        source_root_dir=SOURCE_ROOT_DIR
    )
    code = subprocess.call(cmd, shell=True)
    assert code == 0


def main():
    """
    脚本入口函数
    """
    args = parse_args()
    if args.device and args.fairseq_version:
        dockerfile = os.path.join(args.output_path, "Dockerfile")
        generate_dockerfile(dockerfile,
                            args.device,
                            args.fairseq_version)
        if args.build:
            build_image(dockerfile, IMAGE_NAME, args.version)
    elif args.folder:
        for tag, device, fairseq_version in parse_all_tags(args.folder):
            dockerfile = os.path.join(args.output_path, "Dockerfile-" + tag)
            generate_dockerfile(dockerfile,
                                device,
                                fairseq_version)
            if args.build:
                build_image(dockerfile, IMAGE_NAME, args.version + "-" + tag)
    else:
        raise AttributeError(
            "Please specify device, fairseq_version to generate single dockerfile, "
            "or specify folder to generate all needed dockerfile.")


if __name__ == "__main__":
    main()
