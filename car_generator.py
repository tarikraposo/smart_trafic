import random
import time
from traffic_light import SmartTrafficLight


def generate_random_traffic():
    directions = ["NS", "EW"]
    return random.choice(directions)


def run_traffic_simulation():
    traffic_light = SmartTrafficLight()

    while True:
        # Gera entre 0 e 3 carros por ciclo
        new_cars = random.randint(0, 3)

        for _ in range(new_cars):
            direction = generate_random_traffic()
            traffic_light.add_car(direction)

        traffic_light.run_simulation()
        time.sleep(1)


if __name__ == "__main__":
    run_traffic_simulation()
