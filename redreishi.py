#!/usr/bin/env python3

import nmap
import os
import shutil
import subprocess
import argparse


parser = argparse.ArgumentParser(description="Red Reishi Wine")
parser.add_argument("-t", "--target", type=str, help="Choose a target/host")
parser.add_argument("-d", "--directory", type=str, help="Choose a directory name for outputs")
args, unknown = parser.parse_known_args()


if args.target is None:
    # Define a target here if you don't want to pass it as an arguments
    target = "10.10.163.253"
    print(f"No hostname passed to redreishi, defaulting to {target}\n")
else:
    target = args.target


# Logic for defining what directory to create and store output files in
dir_contents = os.listdir()
if args.directory is None:
    args.directory = f"project {target}"
    print(f"\nNo directory passed as an argument, defaulting to {args.directory}\n")
if args.directory in dir_contents:
    choice = input(f"{args.directory} already found. Overwrite? [y/n]")
    if choice.lower() == 'y':
        print(f"Overwriting directory: {args.directory}")
        shutil.rmtree(args.directory, ignore_errors=True)
    # Don't want to overwrite? Program exits. 
    elif choice.lower() == 'n':
        print('Exiting program.')
        exit()          

os.mkdir(args.directory)
os.chdir(args.directory)
        

rustscan_command = f"rustscan -b 4500 -a {target} --scripts none | tee {target}_rustscan.txt"
# os.system(f"rustscan -b 4500 -a {target} --scripts none | tee {target}_rustscan.txt")
subprocess.Popen(rustscan_command, shell=True).wait()

# open the file and parse for the open ports, add open ports to rustscan_ports string
with open(f"{target}_rustscan.txt") as rustscan_output:
    rustscan_info = rustscan_output.read()
    rustscan_info = rustscan_info.split("\n")
    print(
        f"This is the line that should be grepped and passed onto nmap: {rustscan_info[-2]}"
    )
    rustscan_ports = rustscan_info[-2].split()[2][1:-1]
    rustscan_output.close()


# nmap scan using ports found
nm = nmap.PortScanner()
nmap_command = f"nmap {target} -vvv -p {rustscan_ports} -oA {target}"
subprocess.Popen(nmap_command, shell=True).wait()


with open(f"./{target}.xml") as fd:
    content = fd.read()
    nm.analyse_nmap_xml_scan(content)


# convert xml to html
xsltproc_command = f"xsltproc -o {target}.html /usr/share/nmap/nmap_darkmode.xsl {target}.xml"
subprocess.Popen(xsltproc_command, shell=True) 

ports = []

for host in nm.all_hosts():
    for port_info in nm[host]["tcp"].items():
        ports.append(port_info)


# ftp_auto function will run if 'ftp' is found to be the protocol of a port
def ftp(port_info):
    print("FTP function called successfully")
    command = f"gnome-terminal --tab --title={target}_FTP -- /bin/sh -c 'ftp_auto.py -t {target} -p {int(port_info[0])}; exec bash'"
    # ftp_command = f'xterm -geometry 93x31+0+0 -e bash -c "python3 -i ftp_auto.py -p {int(port_info[0])} -t {nm.all_hosts()[0]} -f {file_name}; bash"'
    subprocess.Popen(command, shell=True)

def ssh(port_info):
    print("SSH function called successfully.")
    command = f"gnome-terminal --tab --title={target}_SSH -- /bin/sh -c 'ssh_auto.py -t {target} -p {int(port_info[0])}; exec bash'"
    subprocess.Popen(command, shell=True)

def smtp(port_info):
    print("SMTP function called successfully.")

def dns(port_info):
    print("DNS function called successfully.")

def http(port_info):
    print("HTTP function called successfully.")
    command = f"gnome-terminal --tab --title={target}_HTTP -- /bin/sh -c 'http_auto.py -t {target} -p {int(port_info[0])}; exec bash'"
    subprocess.Popen(command, shell=True)
    
def pop3(port_info):
    print("SMTP function called successfully.")

def smb(port_info):
    print("SMB function called successfully.")
    smb_command = f'xterm -geometry 93x31+0+0 -e bash -c "python3 -i off_the_rails.py -p {int(port_info[0])} -t {nm.all_hosts()[0]} -f {file_name}; bash"'
    subprocess.Popen(smb_command, shell=True)


# this dictionary ties protocols found in the nmap scan to their corresponding functions.
protocol_functions = {
    "ftp": ftp,
    "ssh": ssh,
    "smtp": smtp,
    "dns": dns,
    "http": http,
    "pop3": pop3,
    "microsoft-ds": smb,
    "netbios-ssn": smb,
}

for port_info in ports:
    # for each port check to see if there is a function for each protocol found in the loop.
    try:
        protocol_functions[port_info[1]["name"]](port_info)
    except:
        pass

ports
