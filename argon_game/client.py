import pygame
import socket
import json
import sys

HOST = '10.10.8.223'
PORT = 5555

# Connect to the MMORPG Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except Exception as e:
    print(f"Could not connect to server at {HOST}:{PORT}. Did you start server.py first?")
    sys.exit()

# Read assigned Player ID
buffer = ""
while "\n" not in buffer:
    buffer += client.recv(1024).decode()
line, buffer = buffer.split("\n", 1)
my_id = json.loads(line)["id"]

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Pythonia MMORPG - Connected as Hero_{my_id}")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14, bold=True)
ui_font = pygame.font.SysFont("Consolas", 15, bold=True)

world_state = {"players": {}, "monsters": {}, "chat": []}
typing_mode = False
chat_input = ""
attack_cooldown = 0
attack_visual_timer = 0

def send_and_receive(msg_dict):
    global buffer, world_state
    try:
        client.send((json.dumps(msg_dict) + "\n").encode())
        while "\n" not in buffer:
            data = client.recv(4096).decode()
            if not data:
                return
            buffer += data
        line, buffer = buffer.split("\n", 1)
        world_state = json.loads(line)
    except Exception as e:
        print("Disconnected from server:", e)
        pygame.quit()
        sys.exit()

running = True
while running:
    clock.tick(30)  # 30 FPS
    dx, dy = 0, 0
    attacked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if typing_mode:
                if event.key == pygame.K_RETURN:
                    if chat_input.strip():
                        send_and_receive({"type": "chat", "text": chat_input})
                    chat_input = ""
                    typing_mode = False
                elif event.key == pygame.K_ESCAPE:
                    chat_input = ""
                    typing_mode = False
                elif event.key == pygame.K_BACKSPACE:
                    chat_input = chat_input[:-1]
                else:
                    if len(chat_input) < 45:
                        chat_input += event.unicode
            else:
                if event.key == pygame.K_RETURN:
                    typing_mode = True
                elif event.key == pygame.K_SPACE and attack_cooldown == 0:
                    attacked = True
                    attack_cooldown = 10
                    attack_visual_timer = 5

    if attack_cooldown > 0:
        attack_cooldown -= 1
    if attack_visual_timer > 0:
        attack_visual_timer -= 1

    if not typing_mode:
        keys = pygame.key.get_pressed()
        speed = 6
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += speed

    # Sync with server
    if attacked:
        send_and_receive({"type": "attack"})
    else:
        send_and_receive({"type": "move", "dx": dx, "dy": dy})

    # ================= RENDER WORLD =================
    screen.fill((38, 115, 55))  # Grass background

    # Draw decorative grid lines for world feel
    for gx in range(0, WIDTH, 80):
        pygame.draw.line(screen, (32, 100, 48), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (32, 100, 48), (0, gy), (WIDTH, gy), 1)

    # Draw Monsters
    for m_id, m in world_state.get("monsters", {}).items():
        mx, my = int(m["x"]), int(m["y"])
        # Monster body
        pygame.draw.rect(screen, (200, 45, 45), (mx - 16, my - 16, 32, 32), border_radius=6)
        pygame.draw.rect(screen, (50, 0, 0), (mx - 16, my - 16, 32, 32), 2, border_radius=6)
        
        # Monster Name
        m_label = font.render(m["type"], True, (255, 220, 220))
        screen.blit(m_label, (mx - m_label.get_width() // 2, my - 38))
        
        # Monster HP Bar
        hp_ratio = max(0, m["hp"] / m["max_hp"])
        pygame.draw.rect(screen, (40, 40, 40), (mx - 20, my - 24, 40, 6))
        pygame.draw.rect(screen, (240, 50, 50), (mx - 20, my - 24, int(40 * hp_ratio), 6))

    # Draw Players
    for p_id, p in world_state.get("players", {}).items():
        px, py = int(p["x"]), int(p["y"])
        
        # Draw Sword Swing Aura if attacking
        if (p_id == my_id and attack_visual_timer > 0) or p.get("attacking"):
            pygame.draw.circle(screen, (255, 240, 150), (px, py), 55, 3)

        # Draw Player Character
        pygame.draw.circle(screen, p["color"], (px, py), 18)
        outline_color = (255, 255, 255) if p_id == my_id else (20, 20, 20)
        pygame.draw.circle(screen, outline_color, (px, py), 18, 2)

        # Name & Level Tag
        name_tag = font.render(f"{p['name']} [Lv.{p['level']}]", True, (255, 255, 255))
        screen.blit(name_tag, (px - name_tag.get_width() // 2, py - 42))

        # Player HP Bar
        hp_ratio = max(0, p["hp"] / p["max_hp"])
        pygame.draw.rect(screen, (40, 40, 40), (px - 22, py - 27, 44, 6))
        pygame.draw.rect(screen, (50, 220, 80), (px - 22, py - 27, int(44 * hp_ratio), 6))

    # ================= RENDER HUD & CHAT =================
    # Chat Box Background
    chat_surface = pygame.Surface((420, 155), pygame.SRCALPHA)
    chat_surface.fill((0, 0, 0, 150))
    screen.blit(chat_surface, (10, HEIGHT - 165))

    chats = world_state.get("chat", [])
    for i, msg in enumerate(chats):
        color = (255, 215, 0) if msg.startswith("[Server]") or "LEVEL UP" in msg else (240, 240, 240)
        c_label = font.render(msg, True, color)
        screen.blit(c_label, (18, HEIGHT - 158 + i * 20))

    # Chat Input Line
    if typing_mode:
        input_label = font.render(f"Say: {chat_input}_", True, (100, 255, 100))
    else:
        input_label = font.render("Press [ENTER] to chat | [SPACE] to attack", True, (180, 180, 180))
    screen.blit(input_label, (18, HEIGHT - 32))

    # Top-Left Player Stats HUD
    if my_id in world_state.get("players", {}):
        me = world_state["players"][my_id]
        hud_bg = pygame.Surface((270, 75), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 160))
        screen.blit(hud_bg, (10, 10))

        stat_1 = ui_font.render(f"{me['name']}  |  Level {me['level']}", True, (255, 255, 120))
        stat_2 = ui_font.render(f"HP: {me['hp']}/{me['max_hp']}", True, (100, 255, 120))
        stat_3 = ui_font.render(f"XP: {me['xp']}/{me['max_xp']}   Online: {len(world_state['players'])}", True, (120, 200, 255))
        
        screen.blit(stat_1, (20, 16))
        screen.blit(stat_2, (20, 38))
        screen.blit(stat_3, (20, 58))

    pygame.display.flip()

pygame.quit()