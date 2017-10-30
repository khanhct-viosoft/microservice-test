#!/usr/bin/python
import os.path
import json
import sqlite3
import os


class Task:

    def __init__(self, task_id, context_id, scenarios_id, content):
        self.task_id = task_id
        self.context_id = context_id
        self.scenarios_id = scenarios_id
        self.content = content

    def getTaskId(self):
        return self.task_id

    def setTaskId(self, new_id):
        self.task_id = new_id

    def getContextId(self):
        return self.context_id

    def setContextId(self, new_context_id):
        self.context_id = new_context_id

    def getScenariosId(self):
        return self.scenarios_id

    def setScenariosId(self, new_scenarios_id):
        self.scenarios_id = new_scenarios_id

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.Content = content