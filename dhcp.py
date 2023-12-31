#!/usr/bin/env python3

from Utils import Utils
import os
from pprint import pprint

class dhcp_autoconfiguration(Utils):
    def __init__(self):
        self.config = {
            "network_address": ["", 
                               "l'adresse du réseau", "ip"],
            "netmask": ["", 
                        "le masque du réseau", "ip"],
            "range_first": ["", 
                            "la première IP de la plage à distribuer", "ip"],
            "range_last": ["", 
                          "la dernière IP de la plage à distribuer", "ip"],
            "router": ["", 
                       "le routeur par défaut", "ip"],
            "dns": ["", 
                    "le serveur DNS", "ip"],
            "default_lease_time": ["0", 
                                   "le lease-time par défaut ( en secondes )", "int"],
            "max_lease_time": ["0", 
                               "le lease-time maximum ( en secondes )", "int"],
        }
        self.apt_up()

        self.uninstall_package('UDHCPD')
        
        self.install_package('isc-dhcp-server')

        self.create_copies()

        self.change_listening_interface()

        self.input_dhcp_config_values()

        self.generate_dhcp_config()

    def input_dhcp_config_values(self):
        print("Vous allez devoir rentrer un par un les différents élements afin de configurer le serveur DHCP -> ")
        self.separator()
        for element in self.config.keys():
            alias = self.config[element][1]
            elementType = self.config[element][2]
            while True:
                if elementType == "ip":
                    userInput = input(f"Entrez {alias} -> ")
                    if self.validate_ip_adress(userInput):
                        self.config[element][0]  = userInput
                        break
                    else:
                        print(f"'{userInput}' est un adresse IP invalide. Reessayez.")
                else:
                    userInput = input(f"Entrez {alias} -> ")
                    try:
                        userInput = int(userInput)
                        if 10 < userInput < 2592000:
                            self.config[element][0] = str(userInput)
                            break
                        else:
                            print(f"{alias.capitalize()} doit être compris entre 10 et 2592000 ( 30 jours ). Reessayez.")  
                    except ValueError:
                        print(f"'{userInput}' n'est pas un nombre entier. Reessayez.")
        self.separator(True)

    def generate_dhcp_config(self):
        while True:
            self.dhcpd = [
                f"subnet {self.config['network_address'][0]} netmask {self.config['netmask'][0]} {'{'}",
                f"range {self.config['range_first'][0]} {self.config['range_last'][0]};",
                f"option routers {self.config['router'][0]};",
                f"option domain-name-servers {self.config['dns'][0]};",
                f"default-lease-time {self.config['default_lease_time'][0]};",
                f"max-lease-time {self.config['max_lease_time'][0]};",
                "}"
            ]

            print("Voici la configuration DHCP générée : ")
            self.separator()
            pprint(self.dhcpd)
            self.separator(True)
            if self.ask("Souhaitez-vous la modifier?"):
                self.input_dhcp_config_values()
                pass
            else:
                while True:
                    if self.ask("Souhaitez-vous pousser la configuration dans le fichier /etc/dhcp/dhcpd.conf?"):
                        try:
                            with open("/etc/dhcp/dhcpd.conf", "w") as file:
                                for line in self.dhcpd:
                                    file.write(line + "\n")
                                break
                        except FileNotFoundError:
                            print("Le fichier /etc/dhcp/dhcpd.conf n'as pas pu être trouvé.")
                        except:
                            print("Une erreur est survenue lors de la modification du fichier /etc/dhcp/dhcpd.conf")
                    else:
                        try:
                            with open("./saves/autogenerated-dhcpd.txt", "w") as file:
                                for line in self.dhcpd:
                                    file.write(line + "\n")
                                print("La configuration a été sauvegardée sous le nom 'autogenerated-dhcpd.txt' dans le répertoire ./saves")
                                break
                        except:
                            print("Une erreur est survenue lors de la sauvegarde de la configuration.")
                break

    def create_copies(self):
        if self.ask("Souhaitez-vous créer des copies des fichiers '/etc/dhcp/dhcpd.conf' et '/etc/default/isc-dhcp-server' avant de commencer?"):
            commands = ["mv /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.default",
                        "touch /etc/dhcp/dhcpd.conf",
                        "mv /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.default",
                        "touch /etc/default/isc-dhcp-server",]
            for command in commands:
                os.system(command)

    def change_listening_interface(self):
        if self.ask("Souhaitez-vous modifier l'interface d'écoute du serveur DHCP?"):
            interface = str(input("Entrez le nom de l'interface d'écoute de votre serveur -> "))
            content = [f"INTERFACESv4=\"{interface}\"",
                    "INTERFACESv6=\"\""]
            try:
                with open("/etc/default/isc-dhcp-server", "w") as file:
                    for line in content:
                        file.write(line + "\n")
            except FileNotFoundError:
                print("Le fichier /etc/default/isc-dhcp-server n'as pas pu être trouvé.")
            except:
                print("Une erreur est survenue.")

myConfig = dhcp_autoconfiguration()

