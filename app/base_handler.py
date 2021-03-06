import json
import traceback
import logging

from tornado.web import RequestHandler

logger = logging.getLogger(__name__)


class _BaseHandler(RequestHandler):

    def _get_result_dict(self, **kwargs):
        raise NotImplementedError

    def options(self):
        self.set_status(204)
        self.finish()

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Expose-Headers", "Content-Type")

    def post(self):

        logger.info("收到请求：%s" % self.request.body)
        response_dict = {
            "status": "200",
            "msg": "请求成功",
        }
        try:
            params = json.loads(self.request.body)
            data = self._get_result_dict(**params)
            if data:
                response_dict["data"] = data
        except Exception as e:
            response_dict["status"] = "500"
            response_dict["msg"] = str(e)
            logger.error(traceback.format_exc())
            
        response = json.dumps(response_dict, ensure_ascii=False)
        logger.info("返回内容：%s" % response)
        self.write(response)
