import json
from flask import Flask, request, Response
from api.monitor import handler as monitor_handler

app = Flask(__name__)

# A mock response class to match Vercel's environment
class VercelResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = {}
        self._body = ""

    def send(self, body):
        self._body = body

# A mock request class to match Vercel's environment
class VercelRequest:
    def __init__(self, flask_request):
        self.url = flask_request.url

@app.route("/api/monitor", methods=['GET'])
def monitor_endpoint():
    # Adapt Flask's request/response to the Vercel-style handler
    req = VercelRequest(request)
    res = VercelResponse()
    
    # Call your original handler function
    monitor_handler(req, res)
    
    # Return a Flask-compatible response
    return Response(
        response=res._body,
        status=res.status_code,
        headers=res.headers
    )

if __name__ == "__main__":
    app.run(debug=True)
