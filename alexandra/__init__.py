import json

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, abort

import alexandra.util as util


class Alexa:
    def __init__(self):
        self.intent_map = {}
        self.launch_fn = None
        self.unknown_intent_fn = self._unknown_intent
        self.session_end_fn = None

    def _unknown_intent(self):
        return Alexa.build_response(text="I'm not sure what this means.")

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

            if not util.validate_request_certificate(request) or \
               not util.validate_request_timestamp(body):
                abort(400)

            resp_obj = self.dispatch_request(body)
            return Response(response=json.dumps(resp_obj, indent=4),
                            status=200,
                            mimetype='application/json')

        except HTTPException, exc:
            return exc

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

            return Alexa.build_response()

        abort(400)

    @staticmethod
    def build_response(text=None, ssml=None, session=None, reprompt=False):
        """ Build a dict containing a valid response to an Alexa request.

        If speech output is desired, either of `text` or `ssml` should
        be specified.

        :param text: Plain text speech output to be said by Alexa device.
        :param ssml: Speech output in SSML form.
        :param session: Dict containing key, value pairs to attach to
                        user's session.
        :param reprompt: If true, one of `text`/`ssml` should be set,
                         and will be used as the reprompt speech
        """

        obj = {
            'version': '1.0',
            'shouldEndSession': session is None
        }

        if text or ssml:
            if text:
                output = {'type': 'TEXT', 'text': text}
            elif ssml:
                output = {'type': 'SSML', 'ssml': ssml}

            if reprompt:
                obj['reprompt'] = {'outputSpeech': output}
            else:
                obj['outputSpeech'] = output

        if session is not None:
            obj['sessionAttributes'] = session

        return obj

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
