# alexandra

Python support for Amazon Alexa devices.

Super duper in progress, but here's the gist:


```python

import alexandra


app = alexandra.Application()

@app.launch
def launch_handler():
    return alexandra.respond(
        text='What would you like to do?',
        reprompt=True
    )


@app.intent('MyNameIs')
def set_name_intent(slots, session):
    name = slots['Name']

    return alexandra.respond(
        text="Okay, I won't forget you, %s" % name,
        session={'name': name},
        end_session=False
    )

@app.intent('WhoAmI')
def get_name_intent(slots, session):
    name = session.get('name')

    if name:
        return alexandra.respond(
            text='You are %s, of course!' % name,
            end_session=False
        )

    return alexandra.respond(
        reprompt_text="We haven't met yet! What's your name?",
        end_session=False
    )


if __name__ == '__main__':
    app.run_debug('0.0.0.0', 8080)
```
