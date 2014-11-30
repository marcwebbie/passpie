#!/usr/bin/env python
from __future__ import print_function

import argparse
from pyscrypt import ScryptFile
from pyscrypt.file import InvalidScryptFileFormat

input = raw_input

def task_create(passwords_file_path):
    with open(passwords_file_path, "w") as passwords_file:
        password = input("new password: ")
        scrypt_file = ScryptFile(passwords_file, password, N = 1024, r = 1, p = 1)
        scrypt_file.close()

    print("New passwords file created at: '{}'".format(passwords_file_path))

def task_add(passwords_file_path):
    try:
        password = input("password: ")
        with open(passwords_file_path, "r") as passwords_file:
            scrypt_file = ScryptFile(passwords_file, password=password)
            passwords_content = scrypt_file.read()
    except InvalidScryptFileFormat:
        print("ERROR: Wrong password")
        exit(1)

    # add new password
    item_name = input("name: ")
    item_login = input("login: ")
    item_password = input("password: ")

    with open(passwords_file_path, "w") as passwords_file:
        scrypt_file = ScryptFile(passwords_file, password, N = 1024, r = 1, p = 1)
        line = "{} = login: {}, password: {}\n".format(item_name, item_login, item_password)
        scrypt_file.write(passwords_content + line)
        scrypt_file.close()

def task_print(passwords_file_path):
    try:
        password = input("password: ")
        with open(passwords_file_path, "r") as passwords_file:
            scrypt_file = ScryptFile(passwords_file, password=password)
            print(scrypt_file.read())
    except InvalidScryptFileFormat:
        print("ERROR: Wrong password")
        exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    # parser.add_argument("-s", "--secret", required=True, help="path to secret file")
    parser.add_argument("-p", "--passfile", required=True, help="path to passwords file")
    args = parser.parse_args()

    task_name = "task_{}".format(args.task)
    task = locals()[task_name]
    # secret_file_path = args.secret
    password_file_path = args.passfile
    task(password_file_path)
