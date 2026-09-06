"""
Эмулятор умного устройства (DUT - Device Under Test).

Зачем это нужно:
В реальной работе тестовая станция подключается к настоящему устройству
(например, по serial-порту или по сети) и гоняет тестовые команды.
У нас нет настоящей колонки/ТВ-приставки — поэтому мы сами пишем
"фейковое устройство", которое ведёт себя как настоящее: отвечает
на команды, иногда тупит с таймаутом, иногда шлёт ошибку.

Протокол максимально простой:
- Станция подключается по TCP на порт 9000.
- Отправляет одну строку с командой (текст) + перевод строки \n.
- Устройство отвечает одной строкой в формате JSON + \n.

Поддерживаемые команды:
- PING                -> {"result": "PONG"}
- GET_STATUS          -> {"result": "ok", "firmware": "1.4.2", "uptime_sec": <int>}
- SET_VOLUME <0-100>  -> {"result": "ok", "volume": <int>}  (или ошибка, если вне диапазона)

Специально встроены "неприятности", с которыми реально сталкиваются
на тестовых станциях:
- иногда устройство отвечает не сразу (эмуляция задержки / зависания),
- иногда шлёт ERROR "device busy",
- иногда просто рвёт соединение без ответа.
Это нужно, чтобы в следующем шаге (ядро станции) учиться нормально
обрабатывать таймауты, ретраи и разрывы связи — а не только "счастливый путь".
"""

import json
import random
import socket
import time
import io

HOST = "127.0.0.1"
PORT = 9000

# Вероятности "неприятностей" - потом можно крутить эти цифры,
# чтобы тренировать станцию на разные сценарии отказов.
PROB_SLOW_RESPONSE = 0.15   # ответит, но с задержкой
PROB_BUSY_ERROR = 0.10      # ответит ошибкой "занято"
PROB_CONNECTION_DROP = 0.05  # оборвёт соединение без ответа

START_TIME = time.time()

def handle_command(raw_command: str) -> str | None:
    """
    Разбирает команду и возвращает JSON-строку ответа.
    Возвращает None, если "устройство" решило оборвать связь без ответа.
    """
    command = raw_command.strip()

    # Эмулируем обрыв связи - станция должна уметь это пережить.
    if random.random() < PROB_CONNECTION_DROP:
        return None

    # Эмулируем "устройство занято".
    if random.random() < PROB_BUSY_ERROR:
        return json.dumps({"result": "error", "message": "device busy"})

    # Эмулируем медленный ответ (например, устройство долго грузится).
    if random.random() < PROB_SLOW_RESPONSE:
        time.sleep(random.uniform(1.5, 3.0))

    if command == "PING" or command == "ping":
        return json.dumps({"result": "PONG"})

    if command == "GET_STATUS" or command == "get_status":
        uptime = int(time.time() - START_TIME)
        return json.dumps({"result": "ok", "firmware": "1.4.2", "uptime_sec": uptime})

    if command.startswith("SET_VOLUME") or command.startswith("set_volume"):
        parts = command.split()
        if len(parts) != 2 or not parts[1].isdigit():
            return json.dumps({"result": "error", "message": "bad volume command"})
        volume = int(parts[1])
        if not (0 <= volume <= 100):
            return json.dumps({"result": "error", "message": "volume out of range"})
        return json.dumps({"result": "ok", "volume": volume})

    if command == "STOP" or command == "stop":
        return json.dumps({"result": "STOP"})

    return json.dumps({"result": "error", "message": f"unknown command: {command}"})


def run_server(host: str = HOST, port: int = PORT) -> None:
    with socket.socket() as server_sock: #разобраться что такое socket
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(1)
        print(f"[DUT emulator] Слушаю {host}:{port} ... (Ctrl+C чтобы остановить)")

        while True:
            conn, addr = server_sock.accept()
            shutdown = False
            conn.settimeout(60)
            with conn:
                print(f"[DUT emulator] Подключилась станция: {addr}")
                reader = conn.makefile("r", encoding="utf-8", newline="\n") #Заменить на нормальный буфер
                while True:
                    try:
                        line = reader.readline()
                    except socket.timeout:
                        print("[DUT emulator] Тишина от станции, закрываю соединение")
                        break

                    if not line:
                        break

                    line = line.rstrip("\n")
                    print(f"[DUT emulator] Получена команда: {line!r}")

                    response = handle_command(line)
                    if response is None:
                        print("[DUT emulator] Симулирую обрыв связи")
                        break

                    response_dict = json.loads(response)
                    conn.sendall((response + "\n").encode("utf-8"))

                    if response_dict.get("result") == "STOP":
                        print("[DUT emulator] Завершение работы")
                        shutdown = True
                        break

            if shutdown is True:
                break

if __name__ == "__main__":
    run_server()
