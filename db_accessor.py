"""
DB data access
"""
import json

import pymongo
from bson.objectid import ObjectId

# TODO: SECRET THE PASSWORD = json.load(open('config.json', 'r').read()["db_password"])


def get_id():
    with open('user_info.txt') as config:
        return config.read()


class DBAccessor:
    # DB client
    def __init__(self):
        self.__client = pymongo.MongoClient("mongodb://ruben:4YZivD7je8eUbIQf@cluster0-shard-00-00.ely3j.mongodb.net:27017,cluster0-shard-00-01.ely3j.mongodb.net:27017,cluster0-shard-00-02.ely3j.mongodb.net:27017/?ssl=true&replicaSet=atlas-mh1otq-shard-0&authSource=admin&retryWrites=true&w=majority")
        self.__db = self.__client["myFirstDatabase"]
        self.__devices_ref = self.__db["devices"]
        self.__workflows = self.__db["workflows"]
        self.uid = str(self.__db["users"].find_one({"_id": ObjectId(get_id())}).get('_id'))
        print(self.uid)

    def get_client(self):
        return self.__client

    def update_state(self, username, registers, states):
        return self.__devices_ref.update_one(
            {"username": username},
            {
                "$set": {
                    "shower": registers,
                    "states": states
                }
            }
        )

    def find_workflow(self):
        return self.__workflows.find_one({"username": self.uid})

    def begin_workflow(self, workflow_steps, command):
        return self.__workflows.insert_one(
            {
                "username": self.uid,
                "timer": 0,
                "workflow": command,
                "steps": workflow_steps
            }
        )

    def update_workflow(self, timer, workflow, steps):
        return self.__workflows.update_one(
            {"username": self.uid},
            {
                "$set": {
                    "timer": timer if timer else 0,
                    "workflow": workflow,
                    "steps": steps
                }
            }
        )

    def delete_workflow(self):
        return self.__workflows.delete_one({"username": self.uid})
