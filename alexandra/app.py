from werkzeug.exceptions import abort

from alexandra.util import build_response
from alexandra.wsgi import WsgiApp

class Application:
    def __init__(self):
        self.intent_map = {}
        self.launch_fn = None
        self.unknown_intent_fn = self._unknown_intent
        self.session_end_fn = None

    def create_wsgi_app(self):
        return WsgiApp(self)

    def run_debug(self, host, port):
        from werkzeug.serving import run_simple

        app = self.create_wsgi_app()
        run_simple(host, port, app, use_reloader=True, use_debugger=True)

    def dispatch_request(self, body):
        req_type = body['request']['type']

        if req_type == 'LaunchRequest' and self.launch_fn:
            return self.launch_fn()

        elif req_type == 'IntentRequest':
            intent = body['request']['intent']['name']
            intent_fn = self.intent_map.get(intent, self.unknown_intent_fn)

            slots = {
                slot['name']: slot['value']
                for _, slot in
                body['request']['intent']['slots'].iteritems()
            }

            return intent_fn(slots, body.get('session'))

        elif req_type == 'SessionEndedRequest':
            if self.session_end_fn:
                return self.session_end_fn()

            return build_response()

        abort(400)

    def launch(self, func):
        """Decorator to register a function to be called whenever the
        app receives a LaunchRequest (which happens when someone
        invokes your skill without specifying an intent).
        """

        self.launch_fn = func
        return func

    def intent(self, name):
        """TODO: foobar"""

        # nested decorator so we can have params.
        def _decorator(func):
            self.intent_map[name] = func
            return func

        return _decorator

    def unknown_intent(self, func):
        self.unknown_intent_fn = func
        return func

    def session_end(self, func):
        self.session_end_fn = func
        return func

    def _unknown_intent(self):
        return Alexa.build_response(text="I'm not sure what this means.")
