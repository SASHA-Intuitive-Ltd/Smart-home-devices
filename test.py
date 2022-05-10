"""
Author: Ruben Rudov
Purpose: Basic speech recognition program for using in more advanced tasks later..
"""

# import speech_recognition as sr
#
# recognizer = sr.Recognizer()
# with sr.Microphone() as source:
#     print("Listening...")
#     recognizer.adjust_for_ambient_noise(source)
#     audio = recognizer.listen(source)
#     try:
#         print("Recognizing...")
#         query = recognizer.recognize_google(audio)
#     except sr.UnknownValueError:
#         print("Could not understand audio")
#     print(query.lower())


# import pyModbusTCP.client as c
# HMI_IP_ADDR = '192.168.1.5'
#
# print(help(c.ModbusClient.read_holding_registers))
# cl = c.ModbusClient()
# print(cl.open())
# print(cl.read_holding_registers(1, 1))
# print(cl.close())
#
# from pyModbusTCP.client import ModbusClient
# c = ModbusClient(host='192.168.1.6', port=502, auto_open=True)
#
# regs = c.read_holding_registers(2, 1)
# print("reading register values")
#
# if regs:
#     print(regs)
# else:
#     print("error")
#     c.write_single_coil('D5', True)


# If file exist, remove it
# if os.path.isfile(COMMAND_FILE_PATH):
#     os.remove(COMMAND_FILE_PATH)
#
# # After file removed, create a new commands file and enter the necessary activation
# f = open(COMMAND_FILE_PATH, 'w')
# writer = csv.writer(f)
#
# # Prepare headers
# # header = ['DW1', 'DW2', 'DW3', 'DW4', 'DW5']
# settings = [10, 1, 3, 2, 3]
#
# # Write headers and values to csv file - HMI Recipes format
# writer.writerow(['RCP32-1.0'])
# writer.writerow(settings)
# writer.writerow(COMMANDS[voice_cmd])
#
# # close the file
# f.close()

# from pyModbusTCP.client import ModbusClient
# HMI_IP_ADDR = '192.168.1.6'
# PLC_IP_ADDR = '192.168.1.5'
# PLC_COM_PORT = 502
# client = ModbusClient(host=PLC_IP_ADDR, port=PLC_COM_PORT, auto_open=True)
# print(client.write_single_coil(2048, True))

import os

# play sound
file = "note.wav"
print('playing sound using native player')
os.system("afplay " + file)