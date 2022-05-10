"""
__author__: 'Ruben Rudov'
__purpose__: 'Main function of voice recognition system for smart shower'
"""

# Import modules
import csv      # For handling csv command files
import speech_recognition as sr     # For recognizing commands and write to file
import json     # Save training info in a json file

# Build a constant speech recognizer
RECOGNIZER = sr.Recognizer()


# Main function
def main():
    # Active until user says 'quit'
    while True:
        json_file = open("commands.json", "r")

        db = json.load(json_file)
        print(db)
        json_file.close()  # Closing the file

        with sr.Microphone() as source:
            print("Listening...")

            # Listeners setting
            RECOGNIZER.adjust_for_ambient_noise(source)
            audio = RECOGNIZER.listen(source)

            try:
                # Try recognize speech
                print("Recognizing...")
                query = RECOGNIZER.recognize_google(audio, "he-IL")

                # Print recognition result for debugging
                print(query.lower())

                # If command is quit system, finish loop
                if query.lower() == 'quit':
                    break

                else:
                    dup = db
                    dup[query] = int(input("Enter an address: "))

                    with open("commands.json", "w") as json_file:
                        json.dump(dup, json_file, indent=4)

            except sr.UnknownValueError:
                # Throw exception if error
                print("Could not understand audio")

            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
