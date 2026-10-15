

import socket
import threading
import json
import time
import random
import math

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

players = {}
monsters = {
    f"m_{i}": {
        "x": random.randint(100, 700),
        "y": random.randint(100, 500),
        "hp": 50,
        "max_hp": 50,
        "type": random.choice(["Slime", "Goblin", "Skeleton"])
    } for i in range(6)
}
chat_messages = ["[Server] Welcome to Pythonia MMORPG!"]
lock = threading.Lock()

def handle_client(conn, player_id):
    global players, monsters, chat_messages
    print(f"[CONNECT] Player {player_id} joined.")
    
    with lock:
        players[player_id] = {
            "x": random.randint(200, 600),
            "y": random.randint(200, 400),
            "color": [random.randint(80, 255), random.randint(80, 255), random.randint(80, 255)],
            "hp": 100, "max_hp": 100,
            "level": 1, "xp": 0, "max_xp": 50,
            "name": f"Hero_{player_id}",
            "attacking": False
        }
        chat_messages.append(f"[Server] Hero_{player_id} spawned into the world!")
        if len(chat_messages) > 6:
            chat_messages.pop(0)

    # Send initial player ID to client
    conn.send((json.dumps({"id": player_id}) + "\n").encode())

    buffer = ""
    while True:
        try:
            data = conn.recv(2048).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line:
                    continue
                msg = json.loads(line)

                with lock:
                    if player_id not in players:
                        continue
                    p = players[player_id]

                    if msg["type"] == "move":
                        p["x"] = max(20, min(780, p["x"] + msg["dx"]))
                        p["y"] = max(20, min(580, p["y"] + msg["dy"]))
                        p["attacking"] = False

                    elif msg["type"] == "attack":
                        p["attacking"] = True
                        # Check combat distance against all monsters
                        for m_id, m in list(monsters.items()):
                            dist = math.hypot(p["x"] - m["x"], p["y"] - m["y"])
                            if dist < 65:  # Attack range
                                dmg = 15 + (p["level"] * 5)
                                m["hp"] -= dmg
                                if m["hp"] <= 0:
                                    # Monster defeated! Grant XP and respawn
                                    p["xp"] += 25
                                    chat_messages.append(f"{p['name']} slew a {m['type']}!")
                                    if p["xp"] >= p["max_xp"]:
                                        p["level"] += 1
                                        p["xp"] = 0
                                        p["max_xp"] = int(p["max_xp"] * 1.5)
                                        p["max_hp"] += 25
                                        p["hp"] = p["max_hp"]
                                        chat_messages.append(f"LEVEL UP! {p['name']} is now Lv.{p['level']}!")
                                    
                                    if len(chat_messages) > 6:
                                        chat_messages = chat_messages[-6:]

                                    # Respawn monster elsewhere with scaling HP
                                    m["x"] = random.randint(80, 720)
                                    m["y"] = random.randint(80, 520)
                                    m["max_hp"] = 50 + (p["level"] * 15)
                                    m["hp"] = m["max_hp"]
                                    m["type"] = random.choice(["Slime", "Goblin", "Orc", "Skeleton"])

                    elif msg["type"] == "chat":
                        text = msg["text"].strip()
                        if text:
                            chat_messages.append(f"{p['name']}: {text}")
                            if len(chat_messages) > 6:
                                chat_messages.pop(0)

                    # Send updated world state back to client
                    state = {
                        "players": players,
                        "monsters": monsters,
                        "chat": chat_messages
                    }
                    conn.send((json.dumps(state) + "\n").encode())

        except Exception as e:
            print(f"[ERROR] Player {player_id}: {e}")
            break

    print(f"[DISCONNECT] Player {player_id} left.")
    with lock:
        if player_id in players:
            name = players[player_id]["name"]
            del players[player_id]
            chat_messages.append(f"[Server] {name} disconnected.")
            if len(chat_messages) > 6:
                chat_messages.pop(0)
    conn.close()

def monster_ai_loop():
    """Background thread that moves monsters randomly and attacks nearby players."""
    while True:
        time.sleep(0.4)
        with lock:
            for m_id, m in monsters.items():
                # Random wandering
                m["x"] = max(40, min(760, m["x"] + random.choice([-12, 0, 12])))
                m["y"] = max(40, min(560, m["y"] + random.choice([-12, 0, 12])))

                # Damage players standing too close
                for p_id, p in players.items():
                    dist = math.hypot(p["x"] - m["x"], p["y"] - m["y"])
                    if dist < 35:
                        p["hp"] -= 5
                        if p["hp"] <= 0:
                            # Player death & respawn
                            p["hp"] = p["max_hp"]
                            p["x"], p["y"] = 400, 300
                            p["xp"] = max(0, p["xp"] - 10)
                            chat_messages.append(f"{p['name']} was defeated by a {m['type']}!")
                            if len(chat_messages) > 6:
                                chat_messages.pop(0)

# Start Monster AI thread
threading.Thread(target=monster_ai_loop, daemon=True).start()

print(f"[SERVER STARTED] Listening on {HOST}:{PORT}...")
player_counter = 1
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, str(player_counter)), daemon=True).start()
    player_counter += 1