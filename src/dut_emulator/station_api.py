import sys
import pathlib
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "dut_emulator"))

from fastapi import FastAPI
from pydantic import BaseModel
from station_core import Scenario, DeviceClient, TestRunner, HOST, PORT

app = FastAPI()

class ScenarioIn(BaseModel):
    name: str
    command: str
    expected_key: str
    expected_value: Any

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/info")
def get_info():
    return {
        "ip": "127.0.0.1",
        "port": 9000
        }

@app.post("/run_test")
def post_run_test(scenario: ScenarioIn):
    client = DeviceClient(HOST, PORT)
    runner = TestRunner(client)
    client_scenario = Scenario(scenario.name, scenario.command, scenario.expected_key, scenario.expected_value)
    return runner.run_scenario(client_scenario)