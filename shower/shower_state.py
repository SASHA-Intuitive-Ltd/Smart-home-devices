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

# Commands map by register value key
CURRENT_MAP = {
    0: "off",
    1: "head",
    2: "body",
    3: "rinse",
    4: "bidet",
    5: "manual"
}

# Commands list by vocal commands and register addresses list
keys = CURRENT_MAP.values()
registers = [x + 4106 for x in range(8)]
REGISTERS_MAP = dict(zip(keys, registers))
# Debug: print(REGISTERS_MAP)


# Get workflow steps by command key
def get_workflow(command):
    workflows = open("workflows.json", "r")
    workflows_content = json.load(workflows)
    workflows.close()
    return workflows_content[command]


# Class for tracking the workflow live
class Tracker:
    def __init__(self, command):
        # DB Access
        self.access = DBAccessor()

        # Vocal command
        self.command = command.lower()

        # Current time in scenario
        self.timer = 0

        # Workflow steps dict
        self.workflow = get_workflow(command.lower())

    # Track function, insert/update by timer
    def track(self, timer):

        # Set timer
        self.timer = timer

        # If there is no active scenario for this user, create one
        if not self.access.find_workflow():
            self.access.begin_workflow(self.workflow, self.command)

        # If there is an active scenario for this user, update it's timer
        elif self.timer == 0 or self.timer < self.workflow["Finished"]:
            self.access.update_workflow(self.timer, self.command, self.workflow)

        # If finished action, delete scenario and let other device take it's place
        else:
            # TODO: Finished action change to other scenario by other controlling script
            self.access.update_workflow(self.timer, self.command, self.workflow)

    # Print current states
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
        # TODO: Specify finishing scenarios in code.
        # if timer == tracker.workflow["Finished"]:
        #     tracker.track(timer=timer)


if __name__ == '__main__':
    main()
