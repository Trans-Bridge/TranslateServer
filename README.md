# Translation Server
翻译服务器，用于部署翻译模型


## Web API
请求方法 post
```
http://{ip}:{port}/yyq/translate/{domain}/{src_lang}/{tgt_lang}
```
api字段解释
|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
| src_lang  | str | 源语言类型，目前暂时支持 en(英文), zh(中文) |
| tgt_lang  | str | 目标语言类型，目前暂时支持 en(英文), zh(中文)|
| domain | str | 翻译领域，目前暂时支持 general (通用领域) |

请求参数 (body json)
|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
| input | str | 待翻译句子 （限制长度200个字符以内）|

请求示例
```http
POST http://localhost:80/yyq/translate/general/zh/en HTTP/1.1
Content-Type: application/json

{
    "input": "正确使用数据操作，掌握排序与限量"
}
```
返回参数
|  参数名   | 参数类型  |  参数解释 |
|  ----  | ----  |  ----  |
|   code    | str        | 返回状态码  200(翻译成功) 500(翻译错误） |
|    msg   |str| 成功时为“success”其他情形返回错误信息|
| translatioin  | str | 译文，此字段放在data字段内 |
返回示例
```
{
    "status": "200",
    "msg": "success",
    "data": {
        "translation": "Correctly use data operation, master sorting and limit"
    }
}
```