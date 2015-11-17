# alexandra

Python support for Amazon Alexa devices.

Super duper in progress, but here's the gist:


```python

import alexandra


app = alexandra.Application()
name_map = {}


@app.launch
def launch_handler():
    return alexandra.respond(
        reprompt_text='What would you like to do?'
    )


@app.intent('MyNameIs')
def set_name_intent(slots, session):
    name = slots['Name']
    name_map[session.user_id] = name

    return alexandra.respond(text="Okay, I won't forget you, %s" % name)


@app.intent('WhoAmI')
def get_name_intent(slots, session):
    name = name_map.get(session.user_id)

    if name:
        return alexandra.respond(text='You are %s, of course!' % name)

    return alexandra.respond(
        text="I don't know your name!",
        reprompt_text="We haven't met yet! What's your name?",
        end_session=False
    )


if __name__ == '__main__':
    app.run_debug('0.0.0.0', 8080)
```
