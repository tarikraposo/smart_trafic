import PySimpleGUI as sg
from traffic_light import SmartTrafficLight
import time


class TrafficLightGUI:
    def __init__(self):
        self.traffic_light = SmartTrafficLight()

        # Define o layout
        layout = [
            [sg.Text('Semáforo Inteligente', font=('Helvetica', 16))],
            [sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400),
                      background_color='white', key='canvas')],
            [sg.Text('Carros N/S: 0', key='ns_count'), sg.Text('Carros L/O: 0', key='ew_count')],
            [sg.Button('Adicionar Carro N/S'), sg.Button('Adicionar Carro L/O')],
            [sg.Button('Sair')]
        ]

        # Cria a janela
        self.window = sg.Window('Semáforo Inteligente', layout, finalize=True)

        # Obtém o canvas
        self.canvas = self.window['canvas']

        # Desenha as ruas
        self.canvas.draw_rectangle((175, 0), (225, 400), 'gray')
        self.canvas.draw_rectangle((0, 175), (400, 225), 'gray')

        # IDs dos semáforos
        self.ns_light = self.canvas.draw_circle((240, 170), 10, fill_color='red')
        self.ew_light = self.canvas.draw_circle((170, 240), 10, fill_color='red')

    def run(self):
        while True:
            event, values = self.window.read(timeout=2000)

            if event == sg.WIN_CLOSED or event == 'Sair':
                break

            if event == 'Adicionar Carro N/S':
                self.traffic_light.add_car('NS')

            if event == 'Adicionar Carro L/O':
                self.traffic_light.add_car('EW')

            # Atualiza o estado do semáforo
            self.traffic_light.make_decision()

            # Atualiza as cores
            ns_color = 'green' if self.traffic_light.current_green == "NS" else 'red'
            ew_color = 'green' if self.traffic_light.current_green == "EW" else 'red'

            self.canvas.TKCanvas.itemconfig(self.ns_light, fill=ns_color)
            self.canvas.TKCanvas.itemconfig(self.ew_light, fill=ew_color)

            # Atualiza os contadores
            self.window['ns_count'].update(f'Carros N/S: {self.traffic_light.north_south_cars}')
            self.window['ew_count'].update(f'Carros L/O: {self.traffic_light.east_west_cars}')

        self.window.close()


if __name__ == '__main__':
    gui = TrafficLightGUI()
    gui.run()
