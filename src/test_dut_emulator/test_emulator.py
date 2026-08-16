import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "dut_emulator"))

from station_core import DeviceClient, Scenario, TestRunner, HOST, PORT, MAX_RETRIES


def make_runner() -> TestRunner:
    """Собирает станцию для одного теста: клиент + раннер с ретраями."""
    client = DeviceClient(HOST, PORT)
    return TestRunner(client, MAX_RETRIES)

def test_ping():
    scenario = Scenario("Проверяем PING", "ping", "result", "PONG")
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_get_status():
    scenario = Scenario("Проверяем GET_STATUS", "get_status", "result", "ok")
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_set_volume_50():
    scenario = Scenario("Проверяем SET_VOLUME 50", "SET_VOLUME 50", "volume", 50)
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_set_volume_0():
    scenario = Scenario("Проверяем SET_VOLUME 0", "SET_VOLUME 0", "volume", 0)
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_set_volume_100():
    scenario = Scenario("Проверяем SET_VOLUME 100", "SET_VOLUME 100", "volume", 100)
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_set_volume_out_of_range():
    scenario = Scenario(
        "Проверяем SET_VOLUME 101",
        "SET_VOLUME 101",
        "message",
        "volume out of range",
    )
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]


def test_unknown_command():
    scenario = Scenario(
        "Проверяем неизвестную команду",
        "aslidjasldjkajf",
        "message",
        "unknown command: aslidjasldjkajf",
    )
    result = make_runner().run_scenario(scenario)
    assert result["passed"], result["last_response"]