#!/usr/bin/env python3

from Utils import Utils
import os
from pprint import pprint

def myprint(myList):
    print("----------------------")
    for element in myList:
        print(element)
    print("----------------------")

class dns_autoconfiguration(Utils):
    def __init__(self):
        self.autoconfig = True

        self.config = {
            "zone_name": "",
            "symbolic_names": [],
            "canonic_names": [],
            "forwarders": [],
        }

        Utils.apt_up()
        Utils.install_package("bind9")
        self.create_copies()

        self.input_dns_config_values()
        self.generate_dns_config()
        self.save_config_files()
       
    def input_dns_config_values(self):
        '''
        Cette fonction demande à l'utilisateur de saisir les informations nécessaires à la configuraiton du DNS
        ( le nom de la zone, les noms symboliques, les forwarders... )
        '''
        print("Vous allez devoir saisir les différentes informations afin de configurer le serveur DNS.")
        print("Si vous souhaitez le faire par vous-même, tapez 'n' pour sortir du mode d'autoconfiguration")
        if self.ask("Souhaitez-vous ajouter une zone DNS?"):
            self.config["zone_name"] = str(input("Entrez le nom de votre zone DNS -> "))
            while True:
                temp_sname = self.gen_s_name()
                if len(temp_sname) > 0:
                    self.config["symbolic_names"].append(temp_sname)
                    continue
                else:
                    break
            while True:
                if self.ask("Souhaitez-vous ajouter un serveur DNS forwarder dans la configuration?"):
                    print("Pour finir, tapez 'exit'")
                    while True:
                        temp_forwarder = self.ask_ip("du DNS forwarder")
                        if temp_forwarder == 'exit':
                            break
                        else:
                            self.config["forwarders"].append(temp_forwarder)
                else:
                    break
        else:
            self.autoconfig = False
            print("Sortie du mode autoconfiguration")

    def generate_dns_config(self):
        '''
        Cette fonction permet de génerer le contenu des fichiers de configuration suivants :
            /etc/bind/named.conf.local
            /etc/bind/named.conf.options
            /etc/bind/db.zone ( où zone est le nom de zone saisi par l'utilisateur )
        Elle demande ensuite à l'utilisateur s'il souhaite que le script ajoute directement ce contenu dans
        les bons fichiers. Sinon les fichiers de conf seront crées dans le répertoire courant.
        '''
        if not self.autoconfig:
            return

        self.named_conf_local = self.configure_zone()
        self.named_conf_options = self.configure_forwarders()
        self.db_zone = self.configure_db_zone()

        print("named.conf.local : ")
        myprint(self.named_conf_local)

        print("named.conf.options : ")
        myprint(self.named_conf_options)

        print(f"db.{self.config['zone_name']} : ")
        myprint(self.db_zone)

    def save_config_files(self):
        '''
        Cette fonction permet, selon le choix de l'utilisateur, de :
            Générer les fichiers de configuration et les enregistrer dans le répertoire courant
            Générer les fichiers de configuration et les remplacer directement dans la configuration du serveur DNS
        '''
        if self.ask("Souhaitez-vous automatiquement remplacer les fichiers de configuration du serveur DNS par les configuration générées par ce script?"):
            print("Les fichiers de configuration suivants vont être modifiés dans le répertoire /etc/bind: ")

            print("     /ect/bind/named.conf.local")
            Utils.fileWriter("/etc/bind/named.conf.local", self.named_conf_local, mode="a")

            print("     /ect/bind/named.conf.options")
            Utils.fileWriter("/etc/bind/named.conf.options", self.named_conf_options, mode="a")

            print(f"     /ect/bind/db.{self.config['zone_name']}")
            Utils.fileWriter(f"/etc/bind/db.{self.config['zone_name']}", self.db_zone, mode="w")
        else:
            print("Les fichiers de configuration suivants vont être enregistrés dans le répértoire courant : ")

            print("     named.conf.local")
            Utils.fileWriter("./named.conf.local", self.named_conf_local)

            print("     named.conf.options")
            Utils.fileWriter("./named.conf.options", self.named_conf_options)

            print(f"     db.{self.config['zone_name']}")
            Utils.fileWriter(f"./db.{self.config['zone_name']}", self.db_zone)

    def configure_zone(self):
        '''
        Cette fonction permet de génerer les commandes qui permettent de ajouter
        notre zone DNS dans le fichier /etc/bind/named.conf.local
        '''
        return [
            f"zone \"{self.config['zone_name']}\" {'{'}",
            "type master;",
            f"file \"/etc/bind/db.{self.config['zone_name']}\";",
            "};"
        ]

    def configure_forwarders(self):
        '''
        Cette fonction permet de générer le contenu du fichier /etc/bind/named.conf.options
        C'est ici que se trouvent les adresses IP des serveurs DNS "forwarders"
        '''
        forwarders = [
            "forwarders {",
            "INPUT_FORWARDERS",
            "};"
        ]

        indexInputForwarders = forwarders.index("INPUT_FORWARDERS")
        forwardersCount = 0

        for element in self.config["forwarders"]:
            forwarders.insert(indexInputForwarders+1, f"{element};")
            forwardersCount += 1
        
        forwarders.pop(forwarders.index("INPUT_FORWARDERS"))

        return forwarders

    def configure_db_zone(self) -> list:
        '''
        Cette fonction permet de configurer le fichier /etc/bind/db.zone
        ( où zone est le nom de la zone DNS qu'on souhaite créer )
        '''
        db_zone = [
            "$TTL 3h",
            f"@ IN SOA ns.{self.config['zone_name']}. mailaddress.{self.config['zone_name']}. (",
            "2021051701",
            "6H",
            "1H",
            "5D",
            "1D )",
            f"@ IN NS ns.{self.config['zone_name']}.",
            f"@ IN MX 10 mail.{self.config['zone_name']}.",
            "INPUT_CNAME",
            "INPUT_SNAME",
        ]

        indexInputCnames = db_zone.index("INPUT_CNAME")
        cnamesCount = 0

        indexInputSnames = db_zone.index("INPUT_SNAME")
        snamesCount = 0

        for element in self.config["symbolic_names"]:
            print(element)
            if element["cname"]:
                print("there's a cname")
                temp_cname = f"{element['cname']} CNAME {element['name']}"
                db_zone.insert(indexInputCnames+1, temp_cname)
                cnamesCount += 1

            temp_sname = f"{element['name']} A {element['ip']}"
            db_zone.insert(indexInputSnames+1, temp_sname)
            snamesCount += 1

        db_zone.pop(db_zone.index("INPUT_CNAME"))
        db_zone.pop(db_zone.index("INPUT_SNAME"))

        return db_zone

    def gen_s_name(self) -> dict:
        '''
        Cette fonction est utilisée afin de demander à l'utilisateur de saisir
        les informations nécessaires pour générer un nom symbolique :
            myServer A 10.200.13.24
        Elle renvoie un dictionnaire avec toutes les informations nécessaires 
        '''
        s_name_config = {
                    "name": "",
                    "ip": "",
                    "cname": "",
                }
        if self.ask(f"Souhaitez-vous ajouter un nom symbolique dans la zone {self.config['zone_name']}"):
            while True:
                s_name_config["name"] = str(input("Entrez le nom symbolique -> "))
                s_name_config["ip"] = self.ask_ip(f"qui correspond à {s_name_config['name']}")
                s_name_config["cname"] = self.gen_c_name(s_name_config["name"])

                Utils.separator()
                print("Voici la configuration obtenue -> ")
                for key, value in s_name_config.items():
                    print(f"{key} : {value}")
                
                if self.ask(f"Souhaitez-vous la modifier?"):
                    continue
                else:
                    return s_name_config
        else:
            return {}

    def gen_c_name(self, symbolic_name) -> str:
        '''
        Cette fonction est utilisée afin de demander à l'utilisateur de saisir un CNAME :
            DHCP CNAME myServer
        Renvoie un string avec le CNAME, ou alors un string vide "" si jamais l'utilisateur
        ne souhaite pas rajouter de CNAME
        '''
        if self.ask(f"Voulez-vous ajouter un nom canonique au {symbolic_name}?"):
            return str(input("CNAME -> ")) 
        else:
            return ""

    def create_copies(self):
        '''
        Cette fonction crée des copies des fichiers de configuration suivants : 
            /etc/bind/named.conf.local
            /etc/bind/named.conf.options
        '''
        if self.ask("Souhaitez-vous créer des copies des fichiers '/etc/bind/named.conf.local' et '/etc/bind/named.conf.options' avant de commencer?"):
            commands = ["mv /etc/bind/named.conf.local /etc/bind/named.conf.local.default",
                        "touch /etc/bind/named.conf.local",
                        "mv /etc/bind/named.conf.options /etc/bind/named.conf.options.default",
                        "touch /etc/bind/named.conf.options",]
            for command in commands:
                os.system(command)


myConfig = dns_autoconfiguration()