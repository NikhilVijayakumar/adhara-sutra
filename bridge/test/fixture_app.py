"""Representative Python runtime fixture for Electron bridge integration tests."""

import sys

from nikhi.adhara_sutra import Application

app = Application("bridge-fixture", "1.0")


@app.action("greeting.create")
def greeting(payload, context):
    return {"message": f"Hello, {payload.get('name', 'world')}!"}


@app.action("broken.action")
def broken(payload, context):
    raise ValueError("boom")


if __name__ == "__main__":
    raise SystemExit(app.run(persistent="--persistent" in sys.argv[1:]))
