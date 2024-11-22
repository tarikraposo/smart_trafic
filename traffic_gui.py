import tkinter as tk
from traffic_light import TrafficLightSystem
import time
import random


class TrafficLightGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Light System")
        self.running = False
        self.last_car_spawn = time.time()
        self.last_pedestrian_spawn = time.time()

        # Configurações
        self.MIN_CAR_DISTANCE = 40
        self.DECELERATION_ZONE = 80
        self.LANES = 2

        self.traffic_system = TrafficLightSystem()

        # Frame superior
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side="top", fill="x", pady=10)

        # Semáforos e controles
        self.canvas1 = tk.Canvas(self.top_frame, width=200, height=150)
        self.canvas1.pack(side="left", padx=20)

        # Frame para contadores
        self.timer_frame = tk.Frame(self.top_frame)
        self.timer_frame.pack(side="left", padx=20)
        self.timer_label = tk.Label(self.timer_frame, text="", font=('Arial', 12))
        self.timer_label.pack()

        self.start_button = tk.Button(self.timer_frame, text="Iniciar", command=self.toggle_simulation)
        self.start_button.pack(pady=5)

        self.canvas2 = tk.Canvas(self.top_frame, width=200, height=150)
        self.canvas2.pack(side="right", padx=20)

        # Canvas principal
        self.main_canvas = tk.Canvas(root, width=500, height=500, bg='gray')
        self.main_canvas.pack(pady=10)

        # Inicializações
        self.create_roads()
        self.lights1 = self.create_traffic_light(self.canvas1)
        self.lights2 = self.create_traffic_light(self.canvas2)

        self.ns_cars = {lane: [] for lane in range(self.LANES)}
        self.ew_cars = {lane: [] for lane in range(self.LANES)}
        self.pedestrians = []

        self.create_initial_cars()

    def create_roads(self):
        # Ruas com múltiplas faixas
        lane_width = 30

        # Rua vertical (Norte-Sul)
        for lane in range(self.LANES):
            x = 250 + (lane * lane_width)
            self.main_canvas.create_rectangle(x, 0, x + lane_width, 500, fill='darkgray')
            if lane < self.LANES - 1:
                self.main_canvas.create_line(x + lane_width, 0, x + lane_width, 500,
                                             fill='white', dash=(10, 10))

        # Rua horizontal (Leste-Oeste)
        for lane in range(self.LANES):
            y = 250 + (lane * lane_width)
            self.main_canvas.create_rectangle(0, y, 500, y + lane_width, fill='darkgray')
            if lane < self.LANES - 1:
                self.main_canvas.create_line(0, y + lane_width, 500, y + lane_width,
                                             fill='white', dash=(10, 10))

        self.create_crosswalk()

    def create_crosswalk(self):
        # Faixas horizontais
        for i in range(5):
            y = 240 + i * 20
            self.main_canvas.create_rectangle(250, y, 350, y + 10, fill='white')

        # Faixas verticais
        for i in range(5):
            x = 240 + i * 20
            self.main_canvas.create_rectangle(x, 250, x + 10, 350, fill='white')

    def create_traffic_light(self, canvas):
        canvas.create_rectangle(25, 10, 75, 140, fill='gray')
        red = canvas.create_oval(35, 20, 65, 50, fill='darkred')
        yellow = canvas.create_oval(35, 60, 65, 90, fill='darkgoldenrod')
        green = canvas.create_oval(35, 100, 65, 130, fill='darkgreen')
        return {'red': red, 'yellow': yellow, 'green': green}

    def create_initial_cars(self):
        for lane in range(self.LANES):
            self.create_car("NS", lane)
            self.create_car("EW", lane)

    def create_car(self, direction, lane=0):
        car_length = 30
        car_width = 20

        if direction == "NS":
            x = 260 + (lane * 30)
            y = -30
            color = "blue"
            car = self.main_canvas.create_rectangle(x, y, x + car_width, y + car_length, fill=color)
            self.ns_cars[lane].append({
                "shape": car,
                "y": y,
                "speed": 5,
                "slowing": False
            })
        else:  # EW
            x = -30
            y = 260 + (lane * 30)
            color = "red"
            car = self.main_canvas.create_rectangle(x, y, x + car_length, y + car_width, fill=color)
            self.ew_cars[lane].append({
                "shape": car,
                "x": x,
                "speed": 5,
                "slowing": False
            })

    def create_pedestrian(self):
        # Definindo os pontos de spawn seguros nas calçadas
        spawn_points = {
            'left': (220, 240),  # Calçada esquerda
            'right': (330, 240),  # Calçada direita
            'top': (240, 220),  # Calçada superior
            'bottom': (240, 330)  # Calçada inferior
        }

        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            x, y = spawn_points['left']
            direction = 'right'
        elif side == 'right':
            x, y = spawn_points['right']
            direction = 'left'
        elif side == 'top':
            x, y = spawn_points['top']
            direction = 'down'
        else:  # bottom
            x, y = spawn_points['bottom']
            direction = 'up'

        ped = self.main_canvas.create_oval(x, y, x + 10, y + 10, fill='yellow')
        self.pedestrians.append({
            "shape": ped,
            "x": x,
            "y": y,
            "direction": direction,
            "speed": 2
        })

    def move_cars(self):
        states = self.traffic_system.get_states()

        # Movimento Norte-Sul
        for lane in range(self.LANES):
            for i, car in enumerate(self.ns_cars[lane][:]):
                should_move = True
                stop_position = 220  # Ajustado para parar mais atrás do cruzamento
                deceleration_zone = self.DECELERATION_ZONE

                # Verifica distância do carro à frente
                if len(self.ns_cars[lane]) > 1 and i > 0:
                    car_ahead = self.ns_cars[lane][i - 1]
                    if car_ahead["y"] - car["y"] < self.MIN_CAR_DISTANCE:
                        should_move = False

                # Se já passou do ponto de parada, mantém velocidade máxima
                if car["y"] > stop_position:
                    car["speed"] = 5
                    should_move = True
                # Se está antes do ponto de parada
                else:
                    if states["NS"] == "red":
                        if car["y"] >= stop_position - 10:
                            should_move = False
                            car["speed"] = 0
                    elif states["NS"] == "yellow" and stop_position - car["y"] < deceleration_zone:
                        car["speed"] = max(1, car["speed"] - 0.5)
                    else:
                        car["speed"] = 5

                if should_move:
                    self.main_canvas.move(car["shape"], 0, car["speed"])
                    car["y"] += car["speed"]

                    if car["y"] > 500:
                        self.main_canvas.delete(car["shape"])
                        self.ns_cars[lane].remove(car)

        # Movimento Leste-Oeste
        for lane in range(self.LANES):
            for car in self.ew_cars[lane][:]:
                should_move = True
                stop_position = 220  # Posição ajustada do semáforo

                # Verifica distância do carro à frente
                if len(self.ew_cars[lane]) > 1:
                    car_index = self.ew_cars[lane].index(car)
                    if car_index > 0:
                        car_ahead = self.ew_cars[lane][car_index - 1]
                        if car_ahead["x"] - car["x"] < self.MIN_CAR_DISTANCE:
                            should_move = False

                # Se já passou do ponto de parada, mantém velocidade máxima
                if car["x"] > stop_position:
                    car["speed"] = 5
                    should_move = True
                # Se está antes do ponto de parada
                else:
                    if states["EW"] == "red":
                        if car["x"] >= stop_position - 10:
                            should_move = False
                            car["speed"] = 0
                    elif states["EW"] == "yellow" and stop_position - car["x"] < self.DECELERATION_ZONE:
                        car["speed"] = max(1, car["speed"] - 0.5)
                    else:
                        car["speed"] = 5

                if should_move:
                    self.main_canvas.move(car["shape"], car["speed"], 0)
                    car["x"] += car["speed"]

                    if car["x"] > 500:
                        self.main_canvas.delete(car["shape"])
                        self.ew_cars[lane].remove(car)

    def move_pedestrians(self):
        states = self.traffic_system.get_states()

        for ped in self.pedestrians[:]:
            # Define áreas das pistas
            ns_road = (250, 310)  # Área da pista Norte-Sul
            ew_road = (250, 310)  # Área da pista Leste-Oeste

            next_x = ped["x"]
            next_y = ped["y"]

            # Calcula próxima posição
            if ped["direction"] == 'right':
                next_x += ped["speed"]
            elif ped["direction"] == 'left':
                next_x -= ped["speed"]
            elif ped["direction"] == 'down':
                next_y += ped["speed"]
            else:  # up
                next_y -= ped["speed"]

            can_move = True

            # Verifica se vai entrar em alguma pista
            entering_ns_road = (ped["x"] < ns_road[0] and next_x >= ns_road[0]) or \
                               (ped["x"] > ns_road[1] and next_x <= ns_road[1])
            entering_ew_road = (ped["y"] < ew_road[0] and next_y >= ew_road[0]) or \
                               (ped["y"] > ew_road[1] and next_y <= ew_road[1])

            # Só permite iniciar travessia quando o sinal está vermelho
            # Bloqueia início da travessia no amarelo
            if entering_ns_road and states["NS"] in ["yellow", "green"]:
                can_move = False
            if entering_ew_road and states["EW"] in ["yellow", "green"]:
                can_move = False

            # Se já está atravessando, permite continuar
            if (ns_road[0] <= ped["x"] <= ns_road[1]) or \
                    (ew_road[0] <= ped["y"] <= ew_road[1]):
                can_move = True

            if can_move:
                if ped["direction"] == 'right':
                    self.main_canvas.move(ped["shape"], ped["speed"], 0)
                    ped["x"] = next_x
                elif ped["direction"] == 'left':
                    self.main_canvas.move(ped["shape"], -ped["speed"], 0)
                    ped["x"] = next_x
                elif ped["direction"] == 'down':
                    self.main_canvas.move(ped["shape"], 0, ped["speed"])
                    ped["y"] = next_y
                else:  # up
                    self.main_canvas.move(ped["shape"], 0, -ped["speed"])
                    ped["y"] = next_y

            # Remove pedestres que saíram da tela
            if (ped["x"] < 0 or ped["x"] > 500 or
                    ped["y"] < 0 or ped["y"] > 500):
                self.main_canvas.delete(ped["shape"])
                self.pedestrians.remove(ped)

    def should_spawn_car(self):
        current_time = time.time()
        if current_time - self.last_car_spawn >= 4:
            self.last_car_spawn = current_time
            return True
        return False

    def should_spawn_pedestrian(self):
        current_time = time.time()
        if current_time - self.last_pedestrian_spawn >= 6:
            self.last_pedestrian_spawn = current_time
            return True
        return False

    def update_light_colors(self, canvas, lights, state):
        canvas.itemconfig(lights['red'], fill='darkred')
        canvas.itemconfig(lights['yellow'], fill='darkgoldenrod')
        canvas.itemconfig(lights['green'], fill='darkgreen')

        if state == 'red':
            canvas.itemconfig(lights['red'], fill='#ff0000')
        elif state == 'yellow':
            canvas.itemconfig(lights['yellow'], fill='#ffff00')
        elif state == 'green':
            canvas.itemconfig(lights['green'], fill='#00ff00')

    def toggle_simulation(self):
        self.running = not self.running
        self.start_button.config(text="Parar" if self.running else "Iniciar")
        if self.running:
            self.update_display()

    def update_display(self):
        if self.running:
            self.traffic_system.update()
            states = self.traffic_system.get_states()

            # Atualiza semáforos
            self.update_light_colors(self.canvas1, self.lights1, states["NS"])
            self.update_light_colors(self.canvas2, self.lights2, states["EW"])

            # Atualiza contadores
            remaining_time = self.traffic_system.get_remaining_time()
            self.timer_label.config(text=f"Tempo restante: {remaining_time}s")

            # Move veículos e pedestres
            self.move_cars()
            self.move_pedestrians()

            # Spawn de novos elementos
            if self.should_spawn_car():
                for lane in range(self.LANES):
                    self.create_car("NS", lane)
                    self.create_car("EW", lane)

            if self.should_spawn_pedestrian():
                self.create_pedestrian()

            self.root.after(50, self.update_display)

def main():
    root = tk.Tk()
    app = TrafficLightGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
