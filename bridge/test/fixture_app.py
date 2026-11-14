"""Representative Python runtime fixture for Electron bridge integration tests."""

import asyncio
import os
import sys
from pathlib import Path

from nikhi.adhara_sutra import Application

app = Application("bridge-fixture", "1.0")


@app.action("greeting.create")
def greeting(payload, context):
    return {"message": f"Hello, {payload.get('name', 'world')}!"}


@app.action("report.submit")
def submit_report(payload, context):
    return {"job_id": context.jobs.submit("report.generate", payload)}


@app.job("report.generate")
async def generate_report(payload, context):
    return {"message": f"Report for {payload.get('name', 'world')}"}


@app.action("fixture.wait")
async def wait_for_release(payload, context):
    release = Path(os.environ["ADHARA_TEST_RELEASE_FILE"])
    context.emit("fixture.entered", {})
    while not release.exists():
        await asyncio.sleep(0.01)
    context.emit("fixture.finished", {})
    return {"finished": True}


@app.action("broken.action")
def broken(payload, context):
    raise ValueError("boom")


if __name__ == "__main__":
    raise SystemExit(app.run(persistent="--persistent" in sys.argv[1:]))
