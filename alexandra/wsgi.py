import json

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, abort

import alexandra.util as util


class WsgiApp:
    def __init__(self, alexa, validate_requests):
        self.alexa = alexa
        self.validate = validate_requests

    @Request.application
    def __call__(self, request):
        return self.wsgi_app(request)

    def wsgi_app(self, request):
        try:
            if request.method != 'POST':
                abort(400)

            try:
                body = json.loads(request.data)
            except ValueError:
                abort(400)

            if self.validate:
                if not util.validate_request_certificate(request) or \
                   not util.validate_request_timestamp(body):
                    abort(400)

            resp_obj = self.alexa.dispatch_request(body)
            return Response(response=json.dumps(resp_obj, indent=4),
                            status=200,
                            mimetype='application/json')

        except HTTPException, exc:
            return exc
