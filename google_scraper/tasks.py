import json

from celery import Celery
from scrape import Scrape

# celery = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')
celery = Celery('tasks', broker='redis://localhost', backend='redis://localhost')
# celery.conf.update(CELERY_TASK_RESULT_EXPIRES=3600,)
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task
def scrape_data(collection_name, query):
    logger.info("before scraper object")
    scrape = Scrape()
    logger.info("before database")
    try:
        data = scrape.fill_database(collection_name, query)
    except:
        return None
    logger.info("after data")
    from bson import json_util
    return json.dumps(data[0:20], default=json_util.default, ensure_ascii=False)
    # return data[0:20]

