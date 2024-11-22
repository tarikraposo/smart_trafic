import time

class TrafficLight:
    def __init__(self):
        self.state = "red"
        self.is_yellow = False
        self.last_update = time.time() * 1000
        self.green_duration = 7000  # 5 segundos
        self.yellow_duration = 3000  # 2 segundos
        self.red_duration = 10000    # 5 segundos + 1 segundo de delay
        self.transition_delay = 1000  # 1 segundo de delay

    def update(self):
        current_time = time.time() * 1000
        elapsed_time = current_time - self.last_update

        if self.state == "green" and elapsed_time >= self.green_duration:
            self.state = "yellow"
            self.is_yellow = True
            self.last_update = current_time
        elif self.state == "yellow" and elapsed_time >= self.yellow_duration:
            self.state = "red"
            self.is_yellow = False
            self.last_update = current_time
        elif self.state == "red" and elapsed_time >= self.red_duration:
            self.state = "green"
            self.is_yellow = False
            self.last_update = current_time

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        self.last_update = time.time() * 1000

class TrafficLightSystem:
    def __init__(self):
        self.traffic_light = TrafficLight()
        self.current_state = {"NS": "green", "EW": "red"}
        self.time_in_state = 0
        self.traffic_light1 = TrafficLight()
        self.traffic_light2 = TrafficLight()
        self.traffic_light1.set_state("green")
        self.traffic_light2.set_state("red")

    def update(self):
        # Update both traffic lights independently
        self.traffic_light1.update()
        self.traffic_light2.update()

        # Get current states
        ns_state = self.traffic_light1.get_state()
        ew_state = self.traffic_light2.get_state()

        # Update current state dictionary
        self.current_state = {
            "NS": ns_state,
            "EW": ew_state
        }
        self.time_in_state += 100


    def get_states(self):
        return self.current_state

    def get_remaining_time(self):
        current_duration = (self.traffic_light.yellow_duration
                          if self.traffic_light.is_yellow
                          else self.traffic_light.green_duration)
        return max(0, int((current_duration - self.time_in_state) / 1000))
