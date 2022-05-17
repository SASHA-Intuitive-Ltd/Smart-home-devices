"""
DB data access
"""
import json

import pymongo

# TODO: SECRET THE PASSWORD = json.load(open('config.json', 'r').read()["db_password"])


class DBAccessor:

    def __init__(self):
        self.__ref: pymongo.collection = self.__client["device"]

    def get_client(self):
        return self.__client

    def update_state(self, username, registers, states):
        self.__ref

