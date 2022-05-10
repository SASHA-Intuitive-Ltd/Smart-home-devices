"""
__author__: 'Ruben Rudov'
__purpose__: 'Main function of voice recognition system for smart shower'
"""

# Import modules
import csv      # For handling csv command files
import speech_recognition as sr     # For recognizing commands and write to file
import os.path      # For removing files
from pyModbusTCP.client import ModbusClient
import json
import playsound
from gtts import gTTS

RECOGNIZER = sr.Recognizer()

json_file = open("commands.json", "r")
REGISTERS = json.load(json_file)
json_file.close()

# Commands file constant path
COMMAND_FILE_PATH: str = r'C:\Users\rudov\Desktop\commands.csv'

# HMI & PLC IP ADDRESS - if modbus could be useful
HMI_IP_ADDR = '192.168.1.6'
PLC_IP_ADDR = '192.168.1.5'
PLC_COM_PORT = 502


# Write command to csv recipe file according to command type
def write_commands(voice_cmd: str, count: int):
    """
    :param count:
    :param voice_cmd: The given voice command, translated to text
    :return: None
    """
    client = ModbusClient(host=PLC_IP_ADDR, port=PLC_COM_PORT, auto_open=True)

    if not voice_cmd == 'stop':
        say(f'Activating: {voice_cmd}', count)
        # TODO: Save active action3
        # TODO 2: dif Thread for say

    else:
        say("Finishing", count)

    if 'sides' in voice_cmd:
        client.write_single_coil(REGISTERS['left'], True)
        client.write_single_coil(REGISTERS['right'], True)

    else:
        client.write_single_coil(REGISTERS[voice_cmd], True)


def say(text, count: int):
    """
    :param count:
    :param text: str that contains the proffered voice output
    :return: None
    """
    tts = gTTS(text=text, lang="en")
    filename = f"voice{count}.mp3"
    tts.save(filename)  # saves the audio file
    playsound.playsound(filename)
    # os.remove(filename)


# Main function
def main():
    # TODO 1: Add multiple mics functionality
    # TODO 2: Check equivalent words
    # TODO 3: Take down all background noises (Change mic..)
    # TODO 4: Add more commands to REGISTERS
    # Active until user says 'quit'
    count = 0
    while True:
        with sr.Microphone() as source:
            print("Listening...")

            # Listeners setting
            RECOGNIZER.adjust_for_ambient_noise(source)
            audio = RECOGNIZER.listen(source)

            try:
                # Try recognize speech
                print("Recognizing...")
                query = RECOGNIZER.recognize_google(audio)

                # Print recognition result for debugging
                print(query.lower())

                # Generate commands file if command in the possible commands list
                if query.lower() in REGISTERS.keys():
                    write_commands(query.lower(), count)
                # If command is quit system, finish loop
                if query.lower() == 'quit':
                    break

            except sr.UnknownValueError:
                # Throw exception if error
                print("Could not understand audio")

            except Exception as e:
                print(e)

            finally:
                count += 1


if __name__ == '__main__':
    main()
