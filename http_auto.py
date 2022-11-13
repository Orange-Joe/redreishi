#!/usr/bin/env python3

import os
import dill
import argparse
import nmap
import subprocess


parser = argparse.ArgumentParser(description="http_enum")
parser.add_argument("-t", "--target", type=str, help="Choose a target/host")
parser.add_argument("-p", "--port", type=int, help="Choose a port")
parser.add_argument("-f", "--filename", type=str, help="Choose an python-nmap class object file") # Legacy argument
args, unknown = parser.parse_known_args()

http_scan = nmap.PortScanner()
# http_scan.scan(args.target, arguments=f"-p {args.port} -A")
nmap_command = f"nmap {args.target} -vvv -p {str(args.port)} -A -oX {args.target}_{args.port}.xml"
subprocess.Popen(nmap_command, shell=True).wait()
# os.system(f"nmap {args.target} -vvv -p {str(args.port)} -A -oX {args.target}_{args.port}.xml")

with open(f"./{args.target}_{args.port}.xml") as fd:
    content = fd.read()
    http_scan.analyse_nmap_xml_scan(content)



def http_enum():

    while True:

        # Print a quick summary
        print(f"\nFound http protocol on {args.target}, port {args.port}. State: {http_scan[str(args.target)]['tcp'][args.port]['state']}")
        print(f"Product: {http_scan[str(args.target)]['tcp'][args.port]['product']}")
        print(f"Version: {http_scan[str(args.target)]['tcp'][args.port]['version']}")
        print(f"CPE: {http_scan[str(args.target)]['tcp'][args.port]['cpe']}")

        try:
            choice = input(f"""
[1] Open {args.target} in Firefox 
[2] Run forexbuster
[3] Something else
[4] Exit
""")

            # Choice 1 - try to login with specified username/password
            if choice.lower() == str(1):
                os.system(f"firefox {args.target} && exit")
            
            # Choice 2 - try to login with specified username/password and dl all files
            elif choice.lower() == str(2):
                brute_force()

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
        contents = os.listdir('/usr/share/wordlists/dirbuster')
        for i in range(len(contents)):
            print(f"[{i}] {contents[i]}")
        choice = input("Choose a number from the list above or write a full path.\n")
        if choice.isdigit():
            wordlist = contents[int(choice)]
        else:
            wordlist = choice
        root_dir = input("Choose a root directory:\n")
        tasks = str(input("Choose number of tasks to run concurrently:\n"))
        extensions = str(input("Choose extensions, separated by commas with no spaces, or leave blank:\n"))


        if len(extensions) > 0:
            command = f"gnome-terminal --window --title=feroxbuster -- /bin/sh -c 'feroxbuster -u http://{args.target}{root_dir} -w /usr/share/dirbuster/wordlists/{wordlist} -t {tasks} -x {extensions}; exec bash'"
            subprocess.Popen(command, shell=True)
        else:
            command = f"gnome-terminal --window --title=feroxbuster -- /bin/sh -c 'feroxbuster -u http://{args.target}{root_dir} -w /usr/share/dirbuster/wordlists/{wordlist} -t {tasks}; exec bash'"
            subprocess.Popen(command, shell=True)

 
http_enum()

