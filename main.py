"""
__author__: 'Ruben Rudov'
__purpose__: 'Main function of voice recognition system for smart shower'
"""

# Import modules
import time
import speech_recognition as sr     # For recognizing commands and write to file
import os.path      # For removing files
from pyModbusTCP.client import ModbusClient
import json
from gtts import gTTS
import pymongo

# Define speech recognizer
RECOGNIZER = sr.Recognizer()

# Define hebrew oriented commands dictionary
json_file = open("commands.json", "r", encoding="utf8")
REGISTERS = json.load(json_file)
json_file.close()

# Define english oriented commands dictionary
json_file1 = open("commands_eng.json", "r")
REGISTERS_eng = json.load(json_file1)
json_file1.close()

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

# DB client
DATABASE_CLUSTER = pymongo.MongoClient(
    "mongodb://ruben:4YZivD7je8eUbIQf@cluster0-shard-00-00.ely3j.mongodb.net:27017,cluster0-shard-00-01.ely3j.mongodb.net:27017,cluster0-shard-00-02.ely3j.mongodb.net:27017/?ssl=true&replicaSet=atlas-mh1otq-shard-0&authSource=admin&retryWrites=true&w=majority"
)
DATABASE = DATABASE_CLUSTER["myFirstDatabase"]
STATES = DATABASE["devices"]

f_user = open('user_info.txt', 'r')
USERNAME = f_user.read()
f_user.close()


def say(text: str, active_lang: str, count: int):
    """
    :param active_lang:
    :param count:
    :param text: str that contains the proffered voice output
    :return: None
    """
    # Hebrew to English translate dict
    HEB_TO_ENG = {
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

    # Text to speech settings
    tts = gTTS(text=f"Activating: {HEB_TO_ENG[text]}", lang="en-US") if active_lang == 'he' else gTTS(text=f"Activating: {text}", lang="en-US")

    # Audio file saving
    filename = f"voice{count}.mp3"
    tts.save(filename)

    # Play the audio file
    # playsound.playsound(filename)

    # Clean file from memory
    os.remove(filename)


# Write command to csv recipe file according to command type
def write_commands(voice_cmd: str, active_lang: str, count: int):
    """
    :param active_lang: current language (set in plc)
    :param count: files count
    :param voice_cmd: The given voice command, translated to text
    :return: None
    """

    # TODO:
    # if 'צדדים' in voice_cmd:
    #     print("Single coil")
    #     client.write_single_coil(REGISTERS['left'], True)
    #     client.write_single_coil(REGISTERS['right'], True)

    # Write command by lang
    if active_lang == 'he':
        client.write_single_coil(REGISTERS[voice_cmd], True)

    else:
        client.write_single_coil(REGISTERS_eng[voice_cmd], True)


    # Indicate user about command being activated
    # say(voice_cmd, active_lang, count)


def find_query(queries, reg_keys: dict) -> str:
    """
    Function for finding the correct key word by alternatives according to given keys
    :param queries: all possible recognitions
    :param reg_keys: language register keys
    :return: str of query
    """
    for q in queries['alternative']:
        if q['transcript'] in reg_keys:
            return q['transcript'].replace("'", "")


def main():
    # Loop count
    count = 0
    log_file = open('script_log.txt', 'w')
    log_file.write(f"Script activated at: {time.ctime()}")
    log_file.close()

    while True:

        # Read and print current language by M162 state
        read_state = client.read_coils(2210)
        print(read_state)

        # Choose lang according to PLC button state
        lang = "he" if read_state[0] is False else "en-US"
        print(lang)

        # When opening mic as source
        with sr.Microphone() as source:

            # Indicate for debug
            print("Listening...")

            # Listeners setting
            RECOGNIZER.adjust_for_ambient_noise(source)
            audio = RECOGNIZER.listen(source)

            try:
                # Try recognize speech
                print("Recognizing...")

                # Recognize possible options, by audio, current lang and show all options
                queries = RECOGNIZER.recognize_google(
                    audio,
                    language=lang,
                    show_all=True,
                )

                # Print option for debugging
                print(queries)

                # Choose the right option for command
                query = find_query(queries, REGISTERS.keys()) if lang == 'he' else find_query(queries, REGISTERS_eng.keys())

                # Generate commands file if command in the possible commands list

                if query:
                    states = []

                    write_commands(query, lang, count)

                    if lang == 'he':
                        for item in REGISTERS.keys().encode:
                            if query != 'עצור':
                                states.append(False if query != item else True)

                            else:
                                states.append(False)
                    else:
                        for item in REGISTERS_eng.keys():
                            if query != 'stop':
                                states.append(False if query != item else True)

                            else:
                                states.append(False)


                    STATES.update_one({"username": USERNAME},  {
                        "$set": {
                            "shower": [item for item in REGISTERS_eng.keys()],
                            "states": states
                        }
                    })

                else:
                    print("UNKNOWN COMMAND")

            # Speech recognition error
            except sr.UnknownValueError:
                # Throw exception if error
                print("Could not understand audio")

            # Print all exceptions
            except Exception as e:
                print(e)

            # Add to count each loop cycle
            finally:
                count += 1


# Run program
if __name__ == '__main__':
    main()
