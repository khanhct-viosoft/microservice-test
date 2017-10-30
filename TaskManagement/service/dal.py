#!/usr/bin/python
import logging
import os
import sqlite3
from sqlite3 import Error
#from task import Task
#from general import *
from service.general import *


#from general import *
LOG = logging.getLogger(__name__)


HOME_DIR = os.path.expanduser('~')
home_folder = os.environ.get('HOME', None)
if home_folder == None:
    user_name = os.environ.get('USER', None)
    if user_name == None:
        raise ValueError('Can not get home folder.')
    else:
        tm_database = '/home/' + user_name + '/.validium/' + TM_DB
else:
    tm_database = home_folder + '/.validium/' + TM_DB

TASK_FIELDS = ['task_id', 'context_id', 'scenarios_id', 'content']

create_task_table = '''CREATE TABLE if not exists task
    (
    task_id  TEXT   PRIMARY KEY     NOT NULL,
    context_id      TEXT    NOT NULL,
    scenarios_id    TEXT    NOT NULL,
    content         TEXT    NOT NULL,
    FOREIGN KEY (context_id) REFERENCES contexts(context_id),
    FOREIGN KEY (scenarios_id) REFERENCES scenarios(scenarios_id)
    );'''

create_context_table = '''CREATE TABLE if not exists contexts
    (
    context_id  TEXT   PRIMARY KEY     NOT NULL,
    content     TEXT    NOT NULL
    );'''

create_scenarios_table = '''CREATE TABLE if not exists scenarios
    (
    scenarios_id  TEXT   PRIMARY KEY     NOT NULL,
    content     TEXT    NOT NULL
    );'''


class DAL:
    conn = None
    c = None
    @staticmethod
    def init():
        global conn
        global c
        try:
            conn = sqlite3.connect(tm_database)
            c = conn.cursor()
            DAL.create_database()
        except Error as e:
            if conn:
                conn.close()
            if c:
                c.close()
            logging.ERROR(e)

    @staticmethod
    def create_database():
        global c
        try:
            c.execute(create_context_table)
            c.execute(create_scenarios_table)
            c.execute(create_task_table)
            conn.commit()
        except Error as e:
            LOG.info("Oops!, Exceptions occur when creating tables: " + str(e))
            return

        LOG.info("All tables created successfully!\n")

    @staticmethod
    def drop_database():
        try:
            c.execute('drop table task')
            c.execute('drop table contexts')
            c.execute('drop table scenarios')
            conn.commit()
        except Error as e:
            LOG.info("Oops!, Exceptions occur when dropping tables: " + str(e))
            return

        LOG.info("All tables dropped successfully!\n")

    @staticmethod
    def close_connection():
        if conn :
            conn.close()


    @staticmethod
    def insert_table(tbl, row):
        keys = []
        values = []
        for key, value in row.items():
            keys.append(str(key))
            values.append(str(value))

        sql = "INSERT OR IGNORE INTO %s (%s) VALUES (%s)" % (
            tbl, str(keys)[1:-1],
            str(values)[1:-1])
        logging.info(sql + '\n')
        c.execute(sql)
        conn.commit()

    @staticmethod
    def add_task(task):
        values =[task.getTaskId(), task.getContextId(), task.getScenariosId(), task.getContent()]
        sql = "INSERT OR IGNORE INTO task (%s) VALUES (%s)" % (str(TASK_FIELDS)[1:-1], str(values)[1:-1])
        try:
            c.execute(sql)
            conn.commit()
        except Error as e:
            LOG.debug("SQL: " + str(sql))
            LOG.debug("Oops!Exceptions occur when inserting data to task: " + str(e))
            return
        LOG.debug('Insert data to task successfully!')

    @staticmethod
    def get_task_info(task_id):
        sql = "SELECT * from task WHERE task_id=?"
        c.execute(sql, (task_id,))
        rows = c.fetchall()
        if len(rows) != 0:
            return rows[0]
        else:
            return None

    @staticmethod
    def query(keys, tbls, cond):
        results = []
        slt = ','.join(str(e) for e in keys)
        frm = ','.join(str(e) for e in tbls)
        sql = "SELECT %s from %s" % (slt, frm)
        if cond:
            sql += " where %s" % cond
        c.execute(sql)
        rows = c.fetchall()
        # convert sql query result into map
        for row in rows:
            r = {}
            for i, val in enumerate(row):
                r[keys[i]] = val
            results.append(r)

        return results

    @staticmethod
    def query_dict(keys, tbls, cond):
        results = {}
        slt = ','.join(str(e) for e in keys)
        frm = ','.join(str(e) for e in tbls)
        sql = "SELECT %s from %s" % (slt, frm)
        if cond:
            sql += " where %s" % cond
        c.execute(sql)
        rows = c.fetchall()
        # convert sql query result into map
        for row in rows:
            r = {}
            for i, val in enumerate(row):
                r[keys[i]] = val
            results.update(r)

        return results

    @staticmethod
    def delete(keys, tbls, cond):
        slt = ','.join(str(e) for e in keys)
        frm = ','.join(str(e) for e in tbls)
        sql = "DELETE %s from %s" % (slt, frm)
        if cond:
            sql += " where %s" % cond
        c.execute(sql)
        conn.commit()

    @staticmethod
    def remove(tbls, cond):
        frm = ','.join(str(e) for e in tbls)
        sql = "DELETE from %s" % frm
        if cond:
            sql += " where %s" % cond
        c.execute(sql)
        conn.commit()

    @staticmethod
    def get_all_tasks():

        c.execute("SELECT * FROM task")
        rows = c.fetchall()

        return rows

#if __name__ == '__main__':
#    DAL.init()
#    t = Task('aaa', 'aaa','sdsds','/root/.validium/yaml/tc_prox_heat_context_l2fwd-2.yaml')
#    DAL.add_task(t)
#    print DAL.get_all_tasks()
    #print DAL.get_task_info('VIO0000000000')
#    DAL.close_connection()
