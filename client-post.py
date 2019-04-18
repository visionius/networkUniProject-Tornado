import requests
import os
import platform
import time
import sys
import platform
import json
import re

PARAMS = CMD = USERNAME = PASSWORD = API = ""
HOST = "localhost"
PORT = "1104"


def __postcr__():
    return "http://"+HOST+":"+PORT+"/"+CMD+"?"


def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
       os.system('clear')

def print_messages(data):
    print(data['tickets'].decode("utf-8"))
    nums=int(re.search(r'\d+', data['tickets'].decode("utf-8")).group())
    sys.stdout.write("%-4s %-20s %-50s %-20s %-30s\n" % ("id", "subject" , "body" , "status" , "date"))
    for i in range(0,nums):
        sys.stdout.write("%-4s %-20s %-50s %-20s %-30s\n" % (json.dumps(data['blocks']['block '+str(i)]['idd'])
                                                            , json.dumps(data['blocks']['block '+str(i)]['subject'])
                                                            , json.dumps(data['blocks']['block '+str(i)]['body'])
                                                            , json.dumps(data['blocks']['block '+str(i)]['status'])
                                                            , json.dumps(data['blocks']['block '+str(i)]['date'])))

def print_codes(data):
    print(data['message'].decode("utf-8"))
    print(data['code'].decode("utf-8"))

def show_func():
    print("USERNAME : "+USERNAME+"\n"+"API : " + API)
    if USERNAME=='root':
        print("""What Do You Prefer To Do :
        1. See all tickets
        2. Send response to a ticket id
        3. Change ticket status with id
        4. Logout
        5. Exit
        """)
    else:
        print("""What Do You Prefer To Do :
        1. See your tickets
        2. Change ticket status to close
        3. Send ticket to admin
        4. Logout
        5. Exit
        """)

while True:
    clear()
    print("""WELCOME TO TICKET SYSTEM
    Please Choose What You Want To Do :
    1. signin
    2. signup
    3. exit
    """)
    status = sys.stdin.readline()
    if status[:-1] == '1':
        clear()
        while True:
            clear()
            print("USERNAME : ")
            USERNAME = sys.stdin.readline()[:-1]
            print("PASSWORD : ")
            PASSWORD = sys.stdin.readline()[:-1]
            CMD = "login"
            PARAMS = {'username':USERNAME , 'password':PASSWORD}
            r = requests.post(__postcr__(), params=PARAMS).json()
            if r['code'] == '200':
                clear()
                print("USERNAME AND PASSWORD IS CORRECT\nLogging You in ...")
                API = r['token']
                #time.sleep(1)
                break
            else:
                clear()
                print("USERNAME AND PASSWORD IS INCORRECT\nTRY AGAIN ...")
                #time.sleep(1)
        while True:
            clear()
            show_func()
            func_type = sys.stdin.readline()
            if func_type[:-1] == '1' and USERNAME == 'root':
                clear()
                CMD = "getticketmod"
                PARAMS = {'token':API}
                data = requests.post(__postcr__(), params=PARAMS).json()
                print_messages(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '2' and USERNAME == 'root':
                clear()
                CMD = "restoticketmod"
                print("Enter id of ticket : ")
                idd = sys.stdin.readline()[:-1]
                print("Enter Your Message : ")
                msg = sys.stdin.readline()[:-1]
                PARAMS = {'token':API , 'id':idd , 'body':msg}
                data = requests.post(__postcr__(), params=PARAMS).json()
                print_codes(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '3' and USERNAME == 'root':
                clear()

                print("Enter id of ticket : ")
                idd = sys.stdin.readline()[:-1]
                print("""Enter status of ticket : 
                        1. Open
                        2. Close 
                        3. In progress""")
                status = sys.stdin.readline()[:-1]
                if status == "1":
                    status="open"
                elif status == "2":
                    status = "close"
                elif status == "3":
                    status = "in progress"
                else:
                    status = "0"
                if not status == "0":
                    CMD = "changestatus"
                    PARAMS = {'token':API , 'id':idd, 'status':status}
                    data = requests.post(__postcr__(), params= PARAMS).json()
                    print_codes(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '4' and USERNAME == 'root':
                CMD = "logout"
                PARAMS = {'username' : USERNAME , 'password' : PASSWORD}
                data = requests.post(__postcr__(), params=PARAMS).json()
                print_codes(data)
                break
            if func_type[:-1] == '5':
                sys.exit()
            #############
            if func_type[:-1] == '1' and not USERNAME == 'root':
                clear()
                CMD = "getticketcli"
                PARAMS = {'token':API}
                data = requests.post(__postcr__(), params= PARAMS).json()
                print_messages(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '2' and not USERNAME == 'root':
                clear()
                CMD = "closeticket"
                print("Enter id of ticket : ")
                idd = sys.stdin.readline()[:-1]
                PARAMS = {'token':API , 'id':idd}
                data = requests.post(__postcr__(), params=PARAMS).json()
                print_codes(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '3' and not USERNAME == 'root':
                clear()
                print("Enter your ticket subject : ")
                msg1 = sys.stdin.readline()[:-1]
                print("Enter your ticket body : ")
                msg2 = sys.stdin.readline()[:-1]
                CMD = "sendticket"
                PARAMS = {'token':API , 'subject' : msg1, 'body':msg2}
                data = requests.post(__postcr__(), params= PARAMS).json()
                print_codes(data)
                input("Press Any Key To Continue ...")
            if func_type[:-1] == '4' and not USERNAME == 'root':
                CMD = "logout"
                PARAMS = {'username' : USERNAME , 'password' : PASSWORD}
                data = requests.post(__postcr__(), params=PARAMS).json()
                break
            if func_type[:-1] == '5':
                sys.exit()

    elif status[:-1] == '2':
        clear()
        while True:
            print("To Create New Account Enter The Authentication")
            print("USERNAME : ")
            USERNAME = sys.stdin.readline()[:-1]
            print("PASSWORD : ")
            PASSWORD = sys.stdin.readline()[:-1]
            print("FIRSTNAME : ")
            FIRSTNAME = sys.stdin.readline()[:-1]
            print("LASTNAME : ")
            LASTNAME = sys.stdin.readline()[:-1]
            CMD = "signup"
            clear()
            PARAMS = {'username' : USERNAME , 'password' : PASSWORD , 'firstname' : FIRSTNAME, 'lastname' : LASTNAME}
            r = requests.post(__postcr__(), params= PARAMS).json()
            if str(r['code']) == "200":
                print("Your Acount Is Created\n"+"Your Username :"+USERNAME+"\nYour API : "+r['token'])
                input("Press Any Key To Continue ...")
                break
            else :
                print(r['code']+"\n"+"Try Again")
                input("Press Any Key To Continue ...")
                clear()

    elif status[:-1] == '3':
        sys.exit()
    else:
        print("Wrong Choose Try Again")

