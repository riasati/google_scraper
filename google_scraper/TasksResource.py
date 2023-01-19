import json

import falcon
from celery.result import AsyncResult


class TasksResource(object):

    def on_get(self, req, resp, task_id):
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(result)
