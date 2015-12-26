#!/usr/bin/python
# -*-coding:utf-8-*-

import os
import sys
import locale
import json
import time
import datetime
import copy

from dialog import Dialog


def is_int(val):
    try:
        int(val)
        return True
    except:
        return False


def is_valid(connections, connection, is_add):
    if False == is_add:
        if connection["name"] in connections:
            return (False,  "connection's name is existed!")
    if "" == connection["name"]:
        return (False, "connection's name can't be empty!")
    if "" == connection["host"]:
        return (False, "connection's host can't be empty!")
    if "" == connection["port"]:
        return (False, "connection's port can't be empty!")
    if False == is_int(connection["port"]):
        return (False, "connection's port is not integer!")
    if "" == connection["user"]:
        return (False, "connection's port can't be empty!")

    return (True, "you're successful to add a connection!")


def edit_dialog(dialog, connections, connection, is_add):
    if None == connection:
        connection = {"name": "CUSTOM", "host": "",  "port": "22", "user": "", "passwd": "", "ogin": "", "assword": ""}

    field_order = ["name", "host", "port", "user", "ogin", "assword"]

    is_retry = True
    while True == is_retry:
        dialog.clear()
        old_name = connection["name"]
        connection = copy.copy(connection)

        elements = []
        for i in xrange(len(field_order)):
            elements.append((field_order[i], i + 1, 1, connection[field_order[i]], i + 1, 15, 50, 50))
        title = "A D D - U S E R" if is_add else "E D I T - U S E R"
        code, tags = dialog.form(title, elements, 25, 60, 16, ok_label="Finish", cancel_label="Cancel")

        # Finish
        if Dialog.OK == code:
            print tags
            (name, host, port, user, ogin, assword) = tags
            for i in xrange(len(field_order)):
                connection[field_order[i]] = tags[i]

            (ret, promt) = is_valid(connections, connection, is_add)
            if True == ret:
                first_passwd, second_passwd = (None, "")
                while first_passwd != second_passwd:
                    code, tag = dialog.passwordbox("please input password:")
                    first_passwd = tag
                    if Dialog.OK == code:
                        code, tag = dialog.passwordbox("please input password again:")
                        if Dialog.OK == code:
                            second_passwd = tag
                    else:
                        first_passwd = second_passwd = connection["pass"]
                    connection["pass"] = first_passwd

                # 更新时间戳
                if "timestamp" not in connection:
                    connection["timestamp"] = 0
                connection["timestamp"] = time.mktime(datetime.datetime.now().timetuple())

                connections[connection["name"]] = connection
                if False == is_add and old_name != connection["name"]:
                    del connections[old_name]

            res = dialog.yesno(promt + "\nDo you continue again?", height=10, width=45,
                               yes_label="Yes, I do", no_label="No, I do not")
            if "ok" == res:
                is_retry = True
            else:
                is_retry = False

        # Cancel
        elif Dialog.CANCEL == code:
            print "Cancel"
            is_retry = False

    return connections


def get_latest_connection(connections):
    max_timestamp = -1
    lastest_connection = None
    for (name, connection) in connections.items():
        if "timestamp" not in connection:
            connection["timestamp"] = 0
        if connection["timestamp"] > max_timestamp:
            max_timestamp = connection["timestamp"]
            lastest_connection = connection
    return lastest_connection


def main_dialog(connections):
    dialog = Dialog(dialog="dialog")
    dialog.set_background_title("QSSH Configuration")

    is_exit = False
    while not is_exit:
        names, choices, connection = ([], [], None)
        for (key, value) in connections.items():
            names.append(key)
            names.sort()
        for name in names:
            choices.append((name, "%s@%s" % (connections[name]["user"], connections[name]["host"])))

        dialog.clear()
        code, tag = dialog.menu("connections", choices=([("", "")] if len(choices) <= 0 else choices),
                                extra_button=True, extra_label="Add", ok_label="Edit", cancel_label="Exit")
        # Edit
        if Dialog.OK == code:
            if tag in connections:
                connection = connections[tag]
                print connection
            connections = edit_dialog(dialog, connections, connection, False)
        # Add
        elif Dialog.EXTRA == code:
            connection = get_latest_connection(connections)
            connections = edit_dialog(dialog, connections, connection, True)
        # Cancel
        elif Dialog.CANCEL == code:
            is_exit = True

    return connections


def main():
    # 创建目录
    config_home = os.path.expanduser('~') + "/.qssh"
    if not os.path.exists(config_home):
        os.makedirs(config_home)

    # 读取配置文件
    config_file_path = config_home + "/config.json"
    connections = {}
    if os.path.exists(config_file_path):
        connections = json.load(open(config_file_path, 'r'))

    # 主页面
    connections = main_dialog(connections)

    # 写入配置文件
    with open(config_file_path, 'w') as f:
        f.write(json.dumps(connections))

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    locale.setlocale(locale.LC_ALL, '')
    main()
