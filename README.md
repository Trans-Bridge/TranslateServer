# Translation Server
翻译服务器，用于部署翻译模型

## 安装运行（单机）
### 系统要求：

centos或者ubuntu

### 安装python依赖包
```
pip install -r requirements.txt
```
#### 安装pyltp（可选）
如果原文为中文(zh)的话，需要pyltp中的分句模块支持，可以使用以下命令安装pyltp
```
git clone https://github.com/HIT-SCIR/pyltp.git && \
    cd pyltp && \
    git checkout v0.4.0 && \
    git submodule init && \
    git submodule update && \
    python setup.py install && \
    cd .. && \
    rm -rf pyltp
```
#### 安装fairseq（可选）
如果需要部署的模型是基于fairseq进行训练的话，需要安装pytorch和fairseq。如果不是基于fairseq的话可以跳过此步骤

pytorch安装可以参考[官方文档](https://pytorch.org/)，根据你的软件版本和是否有gpu选择合适的安装命令进行安装。版本选择1.6以上的版本。

安装fairseq命令如下
```
# 由于不同版本的fairseq训练的模型可能造成模型的不兼容，请确保训练和预测所用的fairseq版本相同
git clone https://github.com/pytorch/fairseq.git && \
    cd fairseq && \
    git checkout v0.10.1 && \  
    pip install -i https://pypi.douban.com/simple . && \
    cd .. && \
    rm -rf fairseq
```
### 准备模型

```
mkdir mount
cp config.yaml.template mount/config.yaml
```
根据需求`config.yaml.template`文件配置，配置相关模型的路径

配置文件参数说明请参考[项目配置](docs/项目配置.md)

如何获取模型请参考[模型获取](docs/模型获取.md)

### 启动服务
```
python service.py
```

## 部署
生成dockerfile
```
# 生成gpu运行，fairseq版本为v0.10.1的dockerfile
python docker/generate_docker_file.py docker/dockerfile_gpu --device cuda --fairseq_version v0.10.1
# 生成cpu运行，fairseq Commit版本为265791b727b664d4d7da3abd918a3f6fb70d7337 的dockerfile
python docker/generate_docker_file.py docker/dockerfile --device cpu --fairseq_version 265791b727b664d4d7da3abd918a3f6fb70d7337
```
构建docker
```bash
# cpu版本
docker build -t translate_server_py:latest -f dockerfile ..
# cuda版本
docker build -t translate_server_py:latest_gpu -f dockerfile_gpu ..
```
### 手动启动容器:
`/path/to/mount`目录内应包含模型、配置文件等。具体参考`准备模型`
```
SERVER_PORT=10000
MODEL_FOLDER=/path/to/mount

docker run -p ${SERVER_PORT}:80 -v ${MODEL_FOLDER}:/root/translate_server_py/mount -itd translate_server_py:latest
```
### 使用docker-compose + nginx自动化部署
首先在任意位置创建一个存放模型的工作目录`workspace`，在目录中可以配置多个`mount`目录。
目录的命名需要满足一定的规则，即下文web api地址的格式 `{who}_translate_{domain}_{src_lang}_{tgt_lang}`。
准备好模型之后可以自动生成`docker-compose`，`nginx.conf`文件，并启动docker-compose继续宁部署。
```
bash start.sh /path/to/workspace {image_tag} {serve_port}
```
其中image_tag应当与构建docker image时的tag一致，serve_port 可以任意指定，为nginx对外提供服务的端口。


## Web API
以下API为基于docker-compose以及nginx部署的服务。如果是单机运行,url固定是`http://{ip}:{port}/yyq/translate`

请求方法 post
```
http://{ip}:{port}/{who}/translate/{domain}/{src_lang}/{tgt_lang}
```
api字段解释

|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
| who | str | 模型的类型，比如对于特定领域和语言对，可以部署不同类型的模型|
| src_lang  | str | 源语言类型 en(英文), zh(中文) |
| tgt_lang  | str | 目标语言类型 en(英文), zh(中文)|
| domain | str | 翻译领域，general (通用领域) |

请求参数 (body json)

|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
| method | str | 执行的方法，目前有 "translate", "add\_words", "delete\_words", "show\_words" |
| data | dict | 执行method方法所需要的参数在这个字段中 |
| input | str (可选) | 在method为“translate”时传递该参数。待翻译句子 （限制长度200个字符以内）|
| words | list (可选) | 在method字段为“add\_words”时传递该参数。需要增加的保护词语, list中的每个元素是[原文，译文] |
| delete | list (可选) | 在method字段为“delete\_words”时传递该参数，需要删除的保护词语 |

请求示例（translate 方法）
```http
POST http://localhost:80/yyq/translate/general/zh/en HTTP/1.1
Content-Type: application/json

{
    "method": "translate",
    "data": {
      "input": "正确使用数据操作，掌握排序与限量"
    }
}
```
请求示例（add\_words 方法）
```http
POST http://localhost:80/yyq/translate/general/zh/en HTTP/1.1
Content-Type: application/json

{
    "method": "add_words",
    "data": {
      "words": [
        ["填方", "filling"],
        ["跳线线夹", "jumper clamp"]
      ]
    }
}
```
请求示例 （delete\_words）
```http
POST http://localhost:80/yyq/translate/general/zh/en HTTP/1.1
Content-Type: application/json

{
    "method": "delete_words",
    "data": {
      "delete": [
        "填方",
        "跳线线夹"
      ]
    }
}
```
请求示例 （show\_words）
```http
POST http://localhost:80/yyq/translate/general/zh/en HTTP/1.1
Content-Type: application/json

{
    "method": "show_words"
}
```
返回参数

|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
|   code    | str        | 返回状态码  200(翻译成功) 500(翻译错误） |
|    msg   |str| 成功时为“success”其他情形返回错误信息|
| translatioin  | str | 译文，此字段放在data字段内 |
| words | list | 目前被保护的词，此字段放在data字段内 |

返回示例（translate 方法）
```json
{
    "status": "200",
    "msg": "success",
    "data": {
        "translation": "Correctly use data operation, master sorting and limit"
    }
}
```
返回示例（add\_words 方法）
```json
{
    "status": "200",
    "msg": "success"
}
```
返回示例 （delete\_words）
```json
{
    "status": "200",
    "msg": "success"
}
```
返回示例 （show\_words）
```json
{
    "status": "200",
    "msg": "success",
    "data": {
        "words": [
            ["填方", "filling"],
            ["跳线线夹", "jumper clamp"]
        ]
    }
}
```
