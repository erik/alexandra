alexandra
=========

|Build Status|

Minimal Python library to remove the tedious boilerplate-y parts of
writing Alexa skills. Alexandra is tested against Python 2.7 and 3.5.1.

Alexandra can be used as part of an AWS lambda function or a self-hosted
server. There's a builtin WSGI app if you're in to that kind of thing.

Check out `the api documentation <http://alexandra.rtfd.org/>`__ for
more details on what alexandra can do.

.. code:: python


    import alexandra

    app = alexandra.Application()
    name_map = {}

    @app.launch
    def launch_handler():
        return alexandra.reprompt('What would you like to do?')

    @app.intent('MyNameIs')
    def set_name_intent(slots, session):
        name = slots['Name']
        name_map[session.user_id] = name

        return alexandra.respond("Okay, I won't forget you, %s" % name)

    @app.intent('WhoAmI')
    def get_name_intent(slots, session):
        name = name_map.get(session.user_id)

        if name:
            return alexandra.respond('You are %s, of course!' % name)

        return alexandra.reprompt("We haven't met yet! What's your name?")

    if __name__ == '__main__':
        app.run('0.0.0.0', 8080, debug=True)

installing
----------

Alexandra uses ``pyOpenSSL``, which requires the ``libffi`` library to
compile. Make sure that's installed first.

If you're on OS X, check out `the special
instructions <https://cryptography.io/en/latest/installation/#building-cryptography-on-os-x>`__
for installing the OpenSSL library if you get errors during installation.

And then:

``pip install alexandra``

using alexandra with aws lambda
-------------------------------

Getting an alexandra app running on lambda is much easier than running
your own server, and is probably the right choice unless you need to
access the local network or have some other complication that prevents
you from using the service.

Here's an example:

.. code:: python

    app = alexandra.Application()

    @app.intent('FooBar')
    def foo_bar():
        ...

    # Entry point to our lambda function.
    def lambda_handler(event, context):
        return alexa.dispatch_request(event)

running with uwsgi
------------------

The ``alexandra.Application`` class has a ``run`` method, which is
useful enough for testing purposes and simple projects, but for real
deployments, you'll probably want to use something a little more robust,
such as uWSGI.

Alexandra works with uwsgi in almost exactly the same way Flask does.

.. code:: python

    # skill_module.py

    app = alexandra.Application()
    wsgi_app = app.create_wsgi_app()

    @app.intent('FooBar')
    def foobar():
        ...

The above can be run with uwsgi as
``uwsgi -w skill_module:wsgi_app --http 0.0.0.0:5678``

setting up a web server
-----------------------

Amazon requires a real SSL certificate for skills to be rolled out to
other users, but fortunately for testing and personal projects
self-signed certificates are acceptable.

To make it a bit easier to generate a self signed SSL certificate and
nginx configuration, here's a Python 2.7/3.5.1 compatible
`standalone script <https://gist.github.com/erik/119dd32efc269d6dd5d7>`_ to
generate basic config for a standard unix setup.

After running the script, simply add a ``location`` block to the nginx
config for any new Alexa skills being hosted on the same box.

For example, if there's an alexandra skill running on port 6789, you
would add:

::

    location /some_random_endpoint {
        proxy_pass http://localhost:6789;
    }

.. |Build Status| image:: https://travis-ci.org/erik/alexandra.svg?branch=master
   :target: https://travis-ci.org/erik/alexandra
