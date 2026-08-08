"""
Интерактивный клиент для ручной отправки команд эмулятору устройства.

В отличие от manual_client.py (который отправляет фиксированный список
команд и завершается), этот скрипт даёт тебе печатать команды самому,
одну за другой, сколько захочешь, и сразу видеть ответ эмулятора.

Запускать после того, как в другом терминале запущен emulator.py:
    py interactive_client.py

Чтобы выйти — напечатай exit и нажми Enter.
"""

import json
import socket

HOST = "127.0.0.1"
PORT = 9000


def main() -> None:
    with socket.socket() as sock:
        try:
            sock.connect((HOST, PORT))
            print("Подключился к эмулятору. Печатай команды (PING, GET_STATUS, SET_VOLUME 50, ...).")
            print("Чтобы выйти — напечатай exit")
        except ConnectionRefusedError:
            print("Что-то пошло не так, ошибка 500")
            return

        while True:
            command = input("Команда > ")

            if command.strip().lower() == "exit":
                print("Выхожу.")
                break

            sock.sendall((command + "\n").encode("utf-8"))

            sock.settimeout(5)
            try:
                data = sock.recv(1024)
            except socket.timeout:
                print("<<< Таймаут — устройство не ответило")
                continue

            if not data:
                print("<<< Соединение закрыто устройством без ответа")
                break

            response = json.loads(data.decode("utf-8").strip())
            print(f"<<< Ответ: {json.dumps(response, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
