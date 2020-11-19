"""
服务启动入口
"""
import os
import tornado
import logging
import app

from config import global_config
from logging.handlers import TimedRotatingFileHandler

# 加载所需要的配置
logdir = global_config["logdir"]

def config_logging():

    log_fmt = '%(asctime)s\tFile\"%(filename)s\",line%(lineno)s\t%(levelname)s:%(message)s'
    formatter = logging.Formatter(log_fmt)
    # S 秒，D 天， M 分钟， H 小时，下面代表每间隔一天生成一个日志文件，每10天定时删除，日志文件存放在log目录下，前缀是translation
    log_file_handler = TimedRotatingFileHandler(filename=os.path.join(logdir, "TranslationLog"),
                                                when="D",
                                                interval=1,
                                                backupCount=10)
    log_file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(log_file_handler)


def main():
    config_logging()
    # 对服务的配置问题
    application = tornado.web.Application(
        [(r'/yyq/translate', app.TranslateHandler)]
    )
    http_server = tornado.httpserver.HTTPServer(application)
    # 2. 服务端口
    http_server.listen(80)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
