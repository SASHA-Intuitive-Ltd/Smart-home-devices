"""
Shower state tracker
"""
from db_accessor import DBAccessor
from pyModbusTCP.client import ModbusClient

import json

# Define addresses and paths configs
af = open("addresses.json", "r")
addresses = json.load(af)
af.close()

# Commands file constant path
COMMAND_FILE_PATH: str = addresses["COMMAND_FILE_PATH"]

# HMI & PLC IP ADDRESS - if modbus could be useful
HMI_IP_ADDR = addresses["HMI_IP_ADDR"]
PLC_IP_ADDR = addresses["PLC_IP_ADDR"]
PLC_COM_PORT = addresses["PLC_COM_PORT"]

# Modbus protocol client
client = ModbusClient(host=PLC_IP_ADDR, port=PLC_COM_PORT, auto_open=True)


CURRENT_MAP = {
    0: "off",
    1: "head",
    2: "body",
    3: "rinse",
    4: "bidet",
    5: "dry",
    6: "manual"
}


keys = CURRENT_MAP.values()
registers = [x + 4106 for x in range(8)]
REGISTERS_MAP = dict(zip(keys, registers))
print(REGISTERS_MAP)


def get_workflow(command):
    workflows = open("workflows.json", "r")
    workflows_content = json.load(workflows)
    workflows.close()
    return workflows_content[command]


class Tracker:
    def __init__(self, command):
        self.access = DBAccessor()
        self.command = command.lower()
        self.timer = 0
        self.workflow = get_workflow(command.lower())

    def track(self, timer):

        self.timer = timer

        if self.timer == 0:
            self.access.begin_workflow(self.workflow, self.command)

        else:
            self.access.update_workflow(self.timer)

    def __str__(self):
        print(f"Timer: {self.timer}, Now: {get_workflow(self.command)}")


def main():

    # Create tracker on script running
    current_scenario_key = CURRENT_MAP[client.read_holding_registers(4105, 1)[0]]
    tracker = Tracker(current_scenario_key)
    tracker.track(timer=0)

    while True:
        timer = client.read_holding_registers(REGISTERS_MAP[current_scenario_key], 1)[0]
        tracker.track(timer=timer)

        print(tracker.__str__())

        if timer == tracker.workflow["Finished"]:
            break


if __name__ == '__main__':
    main()