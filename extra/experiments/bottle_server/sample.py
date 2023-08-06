import bottle
from bottle import response
from threading import Thread

app = bottle.Bottle()

value = 0

@bottle.route('<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static')

@bottle.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/')
def index():
    return "Hello, world!"

@app.route('/get')
def getvalue():
    return value

@app.route('/put', method='PUT')
def put_example():
    value = bottle.request.body.read().decode()
    # do something with the data
    return "Received PUT request with data: " + value

def run_app():
    app.run(host='localhost', port=8080)

if __name__ == '__main__':
    thread = Thread(target=run_app)
    thread.start()
