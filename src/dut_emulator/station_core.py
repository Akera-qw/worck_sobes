import json
import socket
from typing import Any, Dict, List, Optional

# Настройки конфигурации
HOST = "127.0.0.1"
PORT = 9000
MAX_RETRIES = 3

class DeviceClient:
    """Класс для взаимодействия с устройством по сети."""
    TRANSIENT_MESSAGE = {"device buse"}  # Костыль, предусмотренный ответ ошибки

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_command(self, command: str) -> Optional[Dict[str, Any]]:
        try:
            with socket.socket() as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                sock.sendall((command + "\n").encode("utf-8"))
                reader = sock.makefile("r", encoding="utf-8", newline="\n")
                line = reader.readline()

                if not line:
                    return None
                return json.loads(line.strip())
        except (OSError, json.JSONDecodeError):
            return None

    def is_transient(self, response: Optional[Dict[str, Any]]) -> bool:
        """Временная ли это неудача (стоит повторить), или окончательная."""
        if response is None:
            return True # связи не было вообще — точно стоит повторить
        return response.get("message") in self.TRANSIENT_MESSAGE

class Scenario:
    """Класс, описывающий отдельный тестовый сценарий."""

    def __init__(self, name: str, command: str, expected_key: str, expected_value: Any):
        self.name = name
        self.command = command
        self.expected_key = expected_key
        self.expected_value = expected_value

    def check_response(self, response: Dict[str, Any]) -> bool:
        """Проверяет, соответствует ли ответ ожиданиям."""
        if not response:
            return False
        return response.get(self.expected_key) == self.expected_value


class TestRunner:
    """Класс для запуска сценариев и формирования отчетов."""

    def __init__(self, client: DeviceClient, max_retries: int = 3):
        self.client = client
        self.max_retries = max_retries
        self.report = [] # Просто список, в который мы кладем словари

    def run_scenario(self, scenario: Scenario) -> Dict[str, Any]:
        """Запускает один сценарий с поддержкой повторных попыток."""
        last_response = None

        for attempt in range(1, self.max_retries + 1):
            response = self.client.send_command(scenario.command)
            last_response = response

            # Временная неудача — не сдаёмся, идём на следующую попытку.
            if self.client.is_transient(response):
                continue

            return {
                "name": scenario.name,
                "passed": scenario.check_response(response),
                "attempts": attempt,
                "last_response": response,
            }

        return {
            "name": scenario.name,
            "passed": False,
            "attempts": self.max_retries,
            "last_response": last_response,
        }

    def run_all(self, scenarios: List[Scenario]) -> List[Dict[str, Any]]:
        """Запускает список сценариев и сохраняет результаты."""
        self.report = [self.run_scenario(s) for s in scenarios]
        return self.report

    def print_report(self) -> None:
        """Выводит результаты тестирования на экран."""
        if not self.report:
            print("Нет результатов для вывода.")
            return

        print("\n=== ОТЧЁТ ===")
        passed_count = 0

        for result in self.report:
            if result["passed"]:
                status = "[ПРОЙДЕН]"
                passed_count += 1
            else:
                status = "[ПРОВАЛЕН]"
            print(f"{status} {result['name']} (попыток: {result['attempts']})")
        print(f"\nИтого: {passed_count}/{len(self.report)} тестов пройдено")


if __name__ == "__main__":
    # Инициализация списка объектов сценариев
    DEFAULT_SCENARIOS = [
        Scenario("Проверка связи (ping)", "ping", "result", "PONG"),
        Scenario("Проверка статуса устройства", "GET_STATUS", "result", "ok"),
        Scenario("Установка громкости 50", "SET_VOLUME 50", "volume", 50),
    ]

    # Создание компонентов системы
    client = DeviceClient(HOST, PORT)
    runner = TestRunner(client, MAX_RETRIES)

    # Запуск тестов и вывод
    runner.run_all(DEFAULT_SCENARIOS)
    runner.print_report()