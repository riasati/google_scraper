import falcon
from wsgiref.simple_server import make_server
from images import ImageResource
from search import SearchResource

app = application = falcon.App()
images = ImageResource()
search = SearchResource()
app.add_route('/images', images)
app.add_route('/search', search)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()