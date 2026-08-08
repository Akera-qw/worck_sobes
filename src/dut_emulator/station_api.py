import sys
import pathlib
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "dut_emulator"))

from fastapi import FastAPI
from pydantic import BaseModel
from station_core import Scenario, DeviceClient, TestRunner, HOST, PORT, DEFAULT_SCENARIOS

app = FastAPI()

class ScenarioIn(BaseModel):
    name: str
    command: str
    expected_key: str
    expected_value: str | int

def make_con():
    client = DeviceClient(HOST, PORT)
    return TestRunner(client,max_retries=1)

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/info")
def get_info():
    return {
        "ip": HOST,
        "port": PORT
        }

@app.post("/run_test")
def post_run_test(scenario: ScenarioIn):
    client_scenario = Scenario(scenario.name, scenario.command, scenario.expected_key, scenario.expected_value)
    return make_con().run_scenario(client_scenario)

@app.post("/run_all_test")
def post_run_all_test():
    return make_con().run_all(DEFAULT_SCENARIOS)
