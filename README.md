# alexandra

Minimal library to remove the tedious boilerplate-y parts of writing Alexa
skills.

Alexandra can be used as part of an AWS lambda function or a self-hosted
server. There's a builtin WSGI app if you're in to that kind of thing.

## example

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
