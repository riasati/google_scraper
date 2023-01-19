import falcon
from wsgiref.simple_server import make_server
from ImagesResource import ImageResource
from SearchResource import SearchResource
from TasksResource import TasksResource

app = application = falcon.App()

images = ImageResource()
search = SearchResource()
tasks = TasksResource()

app.add_route('/images', images)
app.add_route('/search', search)
app.add_route('/tasks/{task_id}', tasks)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()