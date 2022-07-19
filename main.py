import asyncio
import os
import sys

import aioredis
import tornado
from tornado import options
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.options import define, options
from tornado_sqlalchemy import SQLAlchemy

from celsus.handlers import ProjectHandler, UploadHandler, SearchDifferentialAnalysisHandler, FileDownloadHandler, \
    RedisHandler, LoginHandler, AdminHandler, FileColumnHandler, RawDataHandler, DownloadTokenHandler

database_url = os.getenv("Database")

define("port", default=8000, help="Port number")



routes = [
    (r"/api/project/", ProjectHandler),
    (r"/api/upload/", UploadHandler),
    (r"/api/search/", SearchDifferentialAnalysisHandler),
    (r"/api/project/(.*)/", ProjectHandler),
    (r"/api/file/(.*)/(.*)/", FileDownloadHandler),
    (r"/api/redis/", RedisHandler),
    (r"/api/login/", LoginHandler),
    (r"/api/admin/", AdminHandler),
    (r"/api/columns/", FileColumnHandler),
    (r"/api/raw/(.*)/(.*)/", RawDataHandler),
    (r"/api/download/(.*)/", DownloadTokenHandler)

]


settings = {
    "debug": False,
    "autoreload": False,
    "autoescape": True,
    "x-header": True,
    "db": SQLAlchemy(database_url)
}

class CelcusApp(Application):
    def __init__(self):
        if sys.platform.startswith("win32"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        super().__init__(routes, **settings)

    def init_with_loop(self, loop):
        self.redis = loop.run_until_complete(
            aioredis.from_url(os.getenv("REDIS_HOST"), db=1)
        )


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = CelcusApp()
    app.listen(options.port)
    loop = asyncio.get_event_loop()
    app.init_with_loop(loop)
    IOLoop.current().start()