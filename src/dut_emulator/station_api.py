import sys
import pathlib
import httpx

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
    return TestRunner(client,max_retries=3)

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
    delivered = True
    client_scenario = Scenario(scenario.name, scenario.command, scenario.expected_key, scenario.expected_value)
    one_test = make_con().run_scenario(client_scenario)
    try:
        httpx.post('http://127.0.0.1:8100/results', json=one_test)
    except httpx.HTTPError as e:
        print("Не удалось отправить в MES:", e)
        delivered = False
    return {"results": one_test, "mes_delivered": delivered}

@app.post("/run_all_test")
def post_run_all_test():
    all_test = make_con().run_all(DEFAULT_SCENARIOS)
    delivered = True
    try:
        for i in all_test:
            httpx.post('http://127.0.0.1:8100/results', json=i).raise_for_status()
    except httpx.HTTPError as e:
        print("Не удалось отправить в MES:", e)
        delivered = False
    return {"results": all_test, "mes_delivered": delivered}