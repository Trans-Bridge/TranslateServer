# Translation Server
翻译服务器，用于部署翻译模型

## 安装运行（单机）
### 系统要求：

centos或者ubuntu

### 安装python依赖包
```
pip install -r requirements.txt
```
### 准备模型

```
mkdir mount
cp config.yaml.template mount/config.yaml
```
根据需求`config.yaml.template`文件配置，配置相关模型的路径

配置文件参数说明 （TODO）

如何获取模型（TODO）

### 启动服务
```
python service.py
```

## 部署
构建docker
```
docker build -t translate_server_py:latest .
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
