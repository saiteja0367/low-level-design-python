from enum import Enum


class PowerState(Enum):
    PLUGGED = "PLUGGED"
    UNPLUGGED = "UNPLUGGED"


class Display:
    def show_message(self, message):
        return f"DISPLAY,{message}"


class Speaker:
    def speak_message(self, message):
        return f"SPEAKER,{message}"


class Device:
    def __init__(
        self,
        device_id: str,
        power_state: PowerState,
        percentage: int,
        display=None,
        speaker=None
    ):
        self.device_id = device_id
        self.power_state = power_state
        self.percentage = percentage
        self.display = display
        self.speaker = speaker

    def send_message(self, message):
        results = []

        if self.display is not None:
            results.append(self.display.show_message(message))

        if self.speaker is not None:
            results.append(self.speaker.speak_message(message))

        return results


class DeviceCapabilityManager:
    def __init__(self):
        self.devices = {}

    def register_device(self, device_id, plugged_in, charging_percentage, capabilities):
        if plugged_in:
            power_state = PowerState.PLUGGED
        else:
            power_state = PowerState.UNPLUGGED

        if "DISPLAY" in capabilities:
            display = Display()
        else:
            display = None

        if "SPEAKER" in capabilities:
            speaker = Speaker()
        else:
            speaker = None

        device = Device(
            device_id,
            power_state,
            charging_percentage,
            display,
            speaker
        )

        self.devices[device_id] = device

    def update_power_status(self, device_id, plugged_in, charging_percentage):
        device = self.devices[device_id]

        device.power_state = (
            PowerState.PLUGGED if plugged_in else PowerState.UNPLUGGED
        )
        device.percentage = charging_percentage

    def is_plugged_in(self, device_id):
        device = self.devices[device_id]
        return device.power_state == PowerState.PLUGGED

    def get_charging_percentage(self, device_id):
        device = self.devices[device_id]
        return device.percentage

    def send_message(self, device_id, message):
        device = self.devices[device_id]
        return device.send_message(message)


if __name__ == "__main__":
    manager = DeviceCapabilityManager()

    # Example 1: Device with both display and speaker
    manager.register_device(
        "travel-tablet",
        False,
        58,
        ["SPEAKER", "DISPLAY"]
    )

    print(manager.is_plugged_in("travel-tablet"))
    print(manager.get_charging_percentage("travel-tablet"))
    print(manager.send_message("travel-tablet", "Navigation ready"))

    # Example 2: Device with display only
    manager.register_device(
        "kitchen-panel",
        True,
        91,
        ["DISPLAY"]
    )

    print(manager.send_message("kitchen-panel", "Timer finished"))

    # Example 3: Device with speaker only
    manager.register_device(
        "audio-pod",
        True,
        73,
        ["SPEAKER"]
    )

    print(manager.send_message("audio-pod", "Connection complete"))

    manager.update_power_status("audio-pod", False, 69)

    print(manager.is_plugged_in("audio-pod"))
    print(manager.get_charging_percentage("audio-pod"))

    # Example 4: Device with no messaging capabilities
    manager.register_device(
        "sensor-node",
        False,
        27,
        []
    )

    print(manager.send_message("sensor-node", "Reading recorded"))
