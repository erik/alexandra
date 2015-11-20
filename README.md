alexandra
=========

Minimal library to remove the tedious boilerplate-y parts of writing Alexa
skills.

Alexandra can be used as part of an AWS lambda function or a self-hosted
server. There's a builtin WSGI app if you're in to that kind of thing.

Check out [the api documentation](http://alexandra.rtfd.org/) for more details
on what alexandra can do.

```python

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
    app.run_debug('0.0.0.0', 8080)
```

installing
----------

Alexandra uses `pyOpenSSL`, which requires the `libffi` library to
compile. Make sure that's installed first.

`pip install alexandra`


running with uwsgi
------------------

The `alexandra.Application` class has a `run_debug` method, which is useful
enough for testing purposes, but for real deployments, you'll probably want to
use something a little more robust, such as uWSGI.

TODO: write me

setting up a web server
-----------------------

Amazon requires a real SSL certificate for skills to be rolled out to other
users, but fortunately for testing and personal projects self-signed
certificates are acceptable.

You can use
[this hacky script](https://gist.github.com/erik/119dd32efc269d6dd5d7) to
generate a self signed certificate and Nginx config which should work
well-enough for testing purposes.

After running the script, simply add a `location` block to the nginx config for
any new Alexa skills being hosted on the same box.

For example, if there's an alexandra skill running on port 6789, you would add:

```
location /some_random_endpoint {
    proxy_pass http://localhost:6789
}
```


ugh it doesn't work you suck i keep getting invalid requests
---------------

Is your clock set correctly? You're going to need NTP running so your clock
doesn't drift too away from from reality.

Especially relevant if the server is running on a Raspberry Pi or some
similarly underpowered box.
