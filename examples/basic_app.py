"""Run with: PYTHONPATH=src python3 examples/basic_app.py [--persistent]."""

import sys

from nikhi.adhara_sutra import Application

app = Application(name="example", version="0.1.0")


@app.action("greeting.create")
def greet(payload, context):
    return {"message": f"Hello, {payload.get('name', 'world')}!"}


if __name__ == "__main__":
    app.run(persistent="--persistent" in sys.argv[1:])
