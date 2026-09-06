"""
Общие фикстуры для тестов станции.

pytest находит этот файл автоматически - импортировать его не нужно.

Главная задача: поднять эмулятор устройства перед прогоном тестов
и погасить после. Без этого тесты требовали бы, чтобы кто-то заранее
запустил emulator.py руками — на CI такого «кого-то» нет.
"""

import pathlib
import socket
import subprocess
import sys
import time

import pytest

HOST = "127.0.0.1"
PORT = 9000

EMULATOR_PATH = pathlib.Path(__file__).parent.parent / "dut_emulator" / "emulator.py"


def wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Ждёт, пока порт начнёт принимать подключения. True — дождались."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


@pytest.fixture(scope="session", autouse=True)
def emulator():
    """Поднимает эмулятор на время всего прогона тестов."""
    proc = subprocess.Popen(
        [sys.executable, str(EMULATOR_PATH)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not wait_for_port(HOST, PORT):
        proc.terminate()
        proc.wait(timeout=5)
        pytest.fail(f"Эмулятор не поднялся на {HOST}:{PORT} за отведённое время")

    yield  # здесь выполняются все тесты

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
