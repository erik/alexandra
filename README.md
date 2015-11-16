# alexandra

Python support for Amazon Alexa devices.

Super duper in progress, but here's the gist:


```python

import alexandra


app = alexandra.Application()

@app.launch
def launch_handler():
    return alexandra.build_response(
        text='What would you like to do?',
        reprompt=True
    )


@app.intent('MyNameIs')
def set_name_intent(slots, session):
    name = slots['name']

    return alexandra.build_response(
        text="Okay, I won't forget you, %s" % name,
        session={'name': name}
    )

@app.intent('WhoAmI')
def get_name_intent(slots, session):
    name = session.get('name')

    if name:
        return alexandra.build_response(
            text='You are %s, of course!' % name
            session=session
        )

    return alexandra.build_response(
        text="We haven't met yet! What's your name?",
        reprompt=True
    )

if __name__ = '__main__':
    app.run_debug('127.0.0.1', 8080)
```
