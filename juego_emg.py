import pygame
import random
import math
import serial
import serial.tools.list_ports
import threading

# --- CONSTANTS ---
SKY_BLUE, GRASS_GREEN = (135, 206, 235), (34, 139, 34)
WHITE, BLACK = (255, 255, 255), (30, 30, 30)
GREEN, RED, BLUE = (46, 204, 113), (231, 76, 60), (52, 152, 219)
YELLOW, GRAY, PINK = (255, 255, 0), (200, 200, 200), (255, 182, 193)
BROWN, ROCK_GRAY = (100, 100, 100), (80, 80, 80)

class BiofeedbackGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("FLEX & FLY - EMG REHAB")
        self.clock = pygame.time.Clock()
        
        self.font_ui = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.max_amp_A = 1.0  
        self.max_amp_B = 1.0
        self.raw_val_A = 0.0
        self.raw_val_B = 0.0
        self.emg_history = []
        
        # Hardware Setup
        self.serial_port = None
        self.connect_serial()
        
        self.state = "MENU"
        self.game_mode = "COMBINED" 
        
        self.btn_flex = pygame.Rect(250, 180, 300, 50)
        self.btn_ext = pygame.Rect(250, 250, 300, 50)
        self.btn_comb = pygame.Rect(250, 320, 300, 50)
        self.btn_retry = pygame.Rect(150, 400, 200, 50)
        self.btn_menu = pygame.Rect(450, 400, 200, 50)
        
        self.reset_game_data()

    def connect_serial(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "Arduino" in p.description or "USB" in p.description:
                try:
                    self.serial_port = serial.Serial(p.device, 9600, timeout=0.1)
                    thread = threading.Thread(target=self.read_serial_loop, daemon=True)
                    thread.start()
                    break
                except: continue

    def read_serial_loop(self):
        while self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    self.raw_val_A = int(parts[0]) / 1000.0
                    if len(parts) > 1: self.raw_val_B = int(parts[1]) / 1000.0
            except: pass

    def reset_game_data(self, keep_calibration=False):
        self.chicken_x = 400
        self.score = 0
        self.lives = 3
        self.worms = [] 
        self.rocks = [] 
        self.particles = []
        self.msg_timer = 0
        self.base_speed = 4.0
        if not keep_calibration:
            self.raw_val_A = 0.0
            self.raw_val_B = 0.0

    def get_signals(self):
        if not self.serial_port:
            keys = pygame.key.get_pressed()
            self.raw_val_A = min(1.0, self.raw_val_A + 0.1) if keys[pygame.K_RIGHT] else max(0, self.raw_val_A - 0.05)
            self.raw_val_B = min(1.0, self.raw_val_B + 0.1) if keys[pygame.K_LEFT] else max(0, self.raw_val_B - 0.05)

        eff_A = (self.raw_val_A / self.max_amp_A) if self.max_amp_A > 0.01 else 0
        eff_B = (self.raw_val_B / self.max_amp_B) if self.max_amp_B > 0.01 else 0
        self.emg_history.append((eff_A, eff_B))
        if len(self.emg_history) > 150: self.emg_history.pop(0)
        return min(1.0, eff_A), min(1.0, eff_B)

    def create_confetti(self):
        for _ in range(50):
            color = random.choice([RED, GREEN, BLUE, YELLOW, PINK])
            self.particles.append([400, 300, random.uniform(-5, 5), random.uniform(-8, 2), color])

    def draw_emg_box(self, x, y, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 30, 30, 180), (0, 0, w, h), border_radius=5)
        self.screen.blit(surf, (x, y))
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 1, border_radius=5)
        if len(self.emg_history) < 2: return
        margin = 8
        scale_y = h - (2 * margin)
        for i in range(1, len(self.emg_history)):
            x_pos1, x_pos2 = x + (i-1)*(w/150), x + i*(w/150)
            y_a1 = max(y+margin, min(y+h-margin, (y+h-margin)-(self.emg_history[i-1][0]*scale_y)))
            y_a2 = max(y+margin, min(y+h-margin, (y+h-margin)-(self.emg_history[i][0]*scale_y)))
            pygame.draw.line(self.screen, GREEN, (int(x_pos1), int(y_a1)), (int(x_pos2), int(y_a2)), 2)
            y_b1 = max(y+margin, min(y+h-margin, (y+h-margin)-(self.emg_history[i-1][1]*scale_y)))
            y_b2 = max(y+margin, min(y+h-margin, (y+h-margin)-(self.emg_history[i][1]*scale_y)))
            pygame.draw.line(self.screen, BLUE, (int(x_pos1), int(y_b1)), (int(x_pos2), int(y_b2)), 2)

    def draw_chicken(self, x, y, effort):
        pygame.draw.ellipse(self.screen, YELLOW, (x, y, 60, 50))
        wing_y = y + 18 + int(effort * 15)
        pygame.draw.ellipse(self.screen, (241, 196, 15), (x + 10, wing_y, 30, 18))
        pygame.draw.circle(self.screen, BLACK, (x + 45, y + 15), 4)
        pygame.draw.polygon(self.screen, (255, 128, 0), [(x+55, y+20), (x+65, y+25), (x+55, y+30)])

    def draw_worm(self, x, y, offset):
        for i in range(5):
            seg_y = y + math.sin(offset + i * 0.8) * 3
            pygame.draw.circle(self.screen, PINK, (int(x + i * 8), int(seg_y)), 4)

    def draw_rock(self, x, y):
        pygame.draw.circle(self.screen, ROCK_GRAY, (x, y), 15)
        pygame.draw.circle(self.screen, BLACK, (x, y), 15, 2)

    def draw_heart(self, x, y):
        pygame.draw.circle(self.screen, RED, (x, y), 7)
        pygame.draw.circle(self.screen, RED, (x + 10, y), 7)
        pygame.draw.polygon(self.screen, RED, [(x - 7, y + 3), (x + 17, y + 3), (x + 5, y + 15)])

    def handle_play(self, eff_A, eff_B):
        current_speed = self.base_speed + (self.score // 10) * 0.4
        SPEED_MOVE, GRAVITY_FORCE = 16.0, 3.0
        chicken_rect = pygame.Rect(self.chicken_x, 500, 60, 50)
        
        if self.game_mode == "FLEX": self.chicken_x += (eff_A * SPEED_MOVE) - GRAVITY_FORCE
        elif self.game_mode == "EXT": self.chicken_x += GRAVITY_FORCE - (eff_B * SPEED_MOVE)
        elif self.game_mode == "COMBINED": self.chicken_x += (eff_A - eff_B) * SPEED_MOVE
        self.chicken_x = max(0, min(740, self.chicken_x))
        
        if len(self.worms) < 3 and random.random() < 0.02:
            self.worms.append([random.randint(50, 750), 0, random.uniform(0, 10)])

        for w in self.worms[:]:
            w[1] += current_speed; w[2] += 0.2
            self.draw_worm(w[0], w[1], w[2])
            if chicken_rect.colliderect(pygame.Rect(w[0], w[1], 40, 10)):
                self.score += 1
                if self.score % 25 == 0: self.create_confetti(); self.msg_timer = 120 
                self.worms.remove(w)
            elif w[1] > 550: self.worms.remove(w)
            
        rock_prob = 0
        if 25 <= self.score < 50: rock_prob = 0.002
        elif self.score >= 50: rock_prob = 0.008 + ((self.score - 50) // 10) * 0.005
        if random.random() < rock_prob: self.rocks.append([random.randint(50, 750), 0])
                
        for r in self.rocks[:]:
            r[1] += current_speed + 0.8; self.draw_rock(r[0], r[1])
            if chicken_rect.colliderect(pygame.Rect(r[0]-15, r[1]-15, 30, 30)):
                self.lives -= 1; self.rocks.remove(r)
                if self.lives <= 0: self.state = "GAME_OVER"
            elif r[1] > 550: self.rocks.remove(r)

        self.render_ui(eff_A, eff_B)

    def render_ui(self, eff_A, eff_B):
        for p in self.particles[:]:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.2
            pygame.draw.circle(self.screen, p[4], (int(p[0]), int(p[1])), 3)
            if p[1] > 600: self.particles.remove(p)
        if self.msg_timer > 0: self.draw_txt("EXCELLENT CONTROL!", self.font_big, RED, 400, 250); self.msg_timer -= 1
        self.draw_chicken(self.chicken_x, 500, max(eff_A, eff_B))
        self.draw_emg_box(20, 20, 150, 80)
        self.draw_txt("EMG MONITOR", self.font_small, WHITE, 95, 110)
        if self.game_mode in ["FLEX", "COMBINED"]:
            self.draw_bar(180, 20, 100, 15, eff_A, GREEN); self.draw_txt("F", self.font_small, BLACK, 295, 27)
        if self.game_mode in ["EXT", "COMBINED"]:
            y_bar = 45 if self.game_mode == "COMBINED" else 20
            self.draw_bar(180, y_bar, 100, 15, eff_B, BLUE); self.draw_txt("E", self.font_small, BLACK, 295, y_bar+7)
        self.draw_txt(f"WORMS: {self.score}", self.font_ui, BLACK, 700, 30)
        for i in range(self.lives): self.draw_heart(750 - (i * 25), 65)

    def run(self):
        while True:
            self.screen.fill(SKY_BLUE)
            pygame.draw.rect(self.screen, GRASS_GREEN, (0, 550, 800, 50))
            eff_A, eff_B = self.get_signals()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        if self.btn_flex.collidepoint(event.pos): self.game_mode = "FLEX"; self.start_cal()
                        if self.btn_ext.collidepoint(event.pos): self.game_mode = "EXT"; self.start_cal()
                        if self.btn_comb.collidepoint(event.pos): self.game_mode = "COMBINED"; self.start_cal()
                    elif self.state == "GAME_OVER":
                        if self.btn_retry.collidepoint(event.pos): self.reset_game_data(True); self.state = "PLAY"
                        if self.btn_menu.collidepoint(event.pos): self.state = "MENU"
            if self.state == "MENU":
                self.draw_txt("FLEX & FLY: EMG CHALLENGE", self.font_big, BLACK, 400, 80)
                for b, t, c in [(self.btn_flex, "FLEXION (A)", BLUE), (self.btn_ext, "EXTENSION (B)", BLUE), (self.btn_comb, "COMBINED (A-B)", GREEN)]:
                    pygame.draw.rect(self.screen, c, b, border_radius=10); self.draw_txt(t, self.font_ui, WHITE, b.centerx, b.centery)
            elif self.state.startswith("CAL"): self.handle_calibration()
            elif self.state == "PLAY": self.handle_play(eff_A, eff_B)
            elif self.state == "GAME_OVER":
                self.draw_txt("SESSION FINISHED", self.font_big, RED, 400, 200)
                pygame.draw.rect(self.screen, GREEN, self.btn_retry, border_radius=10)
                pygame.draw.rect(self.screen, GRAY, self.btn_menu, border_radius=10)
                self.draw_txt("RETRY", self.font_ui, WHITE, self.btn_retry.centerx, self.btn_retry.centery)
                self.draw_txt("MENU", self.font_ui, BLACK, self.btn_menu.centerx, self.btn_menu.centery)
            pygame.display.flip(); self.clock.tick(60)

    def handle_calibration(self):
        if self.state == "CAL_A":
            self.draw_txt("CALIBRATING MAX FLEXION", self.font_ui, RED, 400, 200)
            if self.raw_val_A > self.max_amp_A: self.max_amp_A = self.raw_val_A
            self.draw_bar(200, 300, 400, 30, self.raw_val_A, GREEN)
            if (pygame.time.get_ticks() - self.timer) > 3000:
                self.state = "CAL_B" if self.game_mode in ["EXT", "COMBINED"] else "PLAY"
                self.timer = pygame.time.get_ticks()
        elif self.state == "CAL_B":
            self.draw_txt("CALIBRATING MAX EXTENSION", self.font_ui, RED, 400, 200)
            if self.raw_val_B > self.max_amp_B: self.max_amp_B = self.raw_val_B
            self.draw_bar(200, 300, 400, 30, self.raw_val_B, BLUE)
            if (pygame.time.get_ticks() - self.timer) > 3000: self.state = "PLAY"; self.reset_game_data(True)

    def start_cal(self):
        self.state = "CAL_A" if self.game_mode != "EXT" else "CAL_B"
        self.timer = pygame.time.get_ticks(); self.max_amp_A, self.max_amp_B = 0.01, 0.01

    def draw_txt(self, t, f, c, x, y):
        img = f.render(t, True, c); self.screen.blit(img, (x - img.get_width()//2, y - img.get_height()//2))

    def draw_bar(self, x, y, w, h, p, c):
        pygame.draw.rect(self.screen, GRAY, (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, c, (x, y, int(w * p), h), border_radius=5)

if __name__ == "__main__":
    BiofeedbackGame().run()