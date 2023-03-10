import json
import falcon

from database import DataBase
from scrape import Scrape
from tasks import scrape_data


class ImageResource:

    # def on_get(self, req, resp):
    #     query = req.get_param('query') or ''
    #     num = req.get_param_as_int('num') or 20
    #     page = req.get_param_as_int('page') or 1
    #     if query == '':
    #         raise falcon.HTTPBadRequest(title='Incomplete URL', description="You have to provide query parameter")
    #
    #     try:
    #         db = DataBase("image")
    #     except:
    #         raise falcon.HTTPInternalServerError()
    #
    #     data = db.get_collection_data(query, num, page)
    #
    #     if len(data) != 0:
    #         from bson import json_util
    #         resp.text = json.dumps(data, default=json_util.default, ensure_ascii=False)
    #     else:
    #         scrape = Scrape()
    #         data = scrape.fill_database("image", query)
    #         from bson import json_util
    #         resp.text = json.dumps(data[0:num], default=json_util.default,  ensure_ascii=False)

    def on_get(self, req, resp):
        query = req.get_param('query') or ''
        num = req.get_param_as_int('num') or 20
        page = req.get_param_as_int('page') or 1
        if query == '':
            raise falcon.HTTPBadRequest(title='Incomplete URL', description="You have to provide query parameter")

        try:
            db = DataBase("image")
        except:
            raise falcon.HTTPInternalServerError()

        data = db.get_collection_data(query, num, page)

        if len(data) != 0:
            from bson import json_util
            body = json.dumps(data[0:num], default=json_util.default, ensure_ascii=False)

            resp.media = {
                "type": "complete",
                "body": body
            }
        else:
            task = scrape_data.delay("image", query)
            resp.media = {
                "type": "task",
                "body": {},
                "taskid": task.id
            }
