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

json_file = open("commands.json", "r", encoding="utf8")
REGISTERS = json.load(json_file)
json_file.close()

json_file1 = open("commands_eng.json", "r")
REGISTERS_eng = json.load(json_file1)
json_file1.close()

# Data
af = open("addresses.json", "r")
addresses = json.load(af)
af.close()

# Commands file constant path
COMMAND_FILE_PATH: str = addresses["COMMAND_FILE_PATH"]

# HMI & PLC IP ADDRESS - if modbus could be useful
HMI_IP_ADDR = addresses["HMI_IP_ADDR"]
PLC_IP_ADDR = addresses["PLC_IP_ADDR"]
PLC_COM_PORT = addresses["PLC_COM_PORT"]


HEB_TO_SAY = {
    "עליון": "Upper",
    "תחתון": "Lower",
    "גב": "Back",
    "ימני": "Right",
    "שמאלי": "Left",
    "ראש": "Hair",
    "בידה": "Bidet",
    "שטיפה": "Rinse",
    "גוף": "Body",
    "ייבוש": "Dry",
    "עצור": "Stop",
}

client = ModbusClient(host=PLC_IP_ADDR, port=PLC_COM_PORT, auto_open=True)


def say(text: str, active_lang: str, count: int):
    """
    :param active_lang:
    :param count:
    :param text: str that contains the proffered voice output
    :return: None
    """
    tts = gTTS(text=f"Activating: {HEB_TO_SAY[text]}", lang="en-US") if active_lang == 'he' else gTTS(text=f"Activating: {text}", lang="en-US")
    filename = f"voice{count}.mp3"
    tts.save(filename)  # saves the audio file
    playsound.playsound(filename)
    os.remove(filename)


# Write command to csv recipe file according to command type
def write_commands(voice_cmd: str, active_lang: str, count: int):
    """
    :param active_lang:
    :param count:
    :param voice_cmd: The given voice command, translated to text
    :return: None
    """

    # TODO:
    # if 'צדדים' in voice_cmd:
    #     print("Single coil")
    #     client.write_single_coil(REGISTERS['left'], True)
    #     client.write_single_coil(REGISTERS['right'], True)

    print("Single coil")
    if active_lang == 'he':
        client.write_single_coil(REGISTERS[voice_cmd], True)

    else:
        client.write_single_coil(REGISTERS_eng[voice_cmd], True)

        say(voice_cmd, active_lang, count)


def find_query(queries, reg_keys: dict) -> str:
    """
    Function for finding the correct key word by alternatives according to given keys
    :param queries: all possible recognitions
    :param reg_keys: language register keys
    :return:
    """
    for q in queries['alternative']:
        if q['transcript'] in reg_keys:
            return q['transcript'].replace("'", "")


# Main function
def main():
    # TODO 1: Add multiple mics functionality
    # TODO 2: Multiple langs by plc reading

    # Active until user says 'quit'
    count = 0
    while True:
        read_state = client.read_coils(2210)
        print(read_state)
        # DEBUG: read_state = 1
        # Choose lang according to PLC button state
        lang = "he" if read_state[0] is False else "en-US"
        print(lang)

        with sr.Microphone() as source:
            print("Listening...")

            # Listeners setting
            RECOGNIZER.adjust_for_ambient_noise(source)
            audio = RECOGNIZER.listen(source)

            try:
                # Try recognize speech
                print("Recognizing...")
                queries = RECOGNIZER.recognize_google(
                    audio,
                    language=lang,
                    show_all=True,
                )

                print(queries)

                query = find_query(queries, REGISTERS.keys()) if lang == 'he' else find_query(queries, REGISTERS_eng.keys())

                # Generate commands file if command in the possible commands list
                if query:
                    write_commands(query, lang, count)

                else:
                    print("UNKNOWN COMMAND")

            except sr.UnknownValueError:
                # Throw exception if error
                print("Could not understand audio")

            except Exception as e:
                print(e)

            finally:
                count += 1


if __name__ == '__main__':
    main()
