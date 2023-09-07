#!/usr/bin/env python3

from Utils import Utils
import os
from pprint import pprint

class http_autoconfiguration(Utils):
    def __init__(self):
        self.config = {
            "name": "",
            "includeIndexFile": True,
        }

        Utils.apt_up()
        Utils.install_package("apache2")
        self.create_copies()

        self.input_http_config_values()
        self.generate_http_config()
        self.save_config_files()

    def input_http_config_values(self):
        '''
        Demande de saisie au clavier des informations de configuration importantes
        '''
        self.config["name"] = str(input("Entrez le du site à créer -> "))
        
        if self.ask("Souhaitez-vous ajouter automatiquement un fichier index.html par défaut?"):
            pass
        else:
             self.config["includeIndexFile"] = False

    def generate_http_config(self):
        '''
        Création du contenu des fichiers de conf
        '''
        self.conf_000_default = [
            "<VirtualHost *:80>",
            "   ServerAdmin webmaster@localhost"
            f"  DocumentRoot /var/www/{self.config['name']}",
            "   ErrorLog ${APACHE_LOG_DIR}/error.log"
            "   CustomLog ${APACHE_LOG_DIR}/access.log combined",
            "</VirtualHost>"
        ]

        if self.config["includeIndexFile"]:
            self.index_html = [
                "<!DOCTYPE html>"
                "<html>",
                "   <head>",
                "       <style>",
                "           body { display: flex; justify-content: center; align-items: center; background-color: #222222; }",
                "           h1 { font-size: 100px; color: white; font-weight: bold; }"
                "       </style>",
                "   </head>",
                "   <body>",
                f"      <h1>Welcome to {self.config['namer']}",
                "   </body>",
                "</html>"
            ]

    def save_config_files(self):
        '''
        Cette fonction permet de génerer le contenu des fichiers de configuration suivants :
            /etc/apache2/000-default.conf
        Si l'utilisateur a choisi de générer un fichier index.html automatiquement,
        le fichier /var/www/nom_du_site sera également crée et configuré
        '''
        self.fileWriter("/etc/apache2/000-default.conf", self.conf_000_default)
        os.system(f"mkdir /var/www/{self.config['name']}")
        if self.config["includeIndexFile"]:
            self.fileWriter(f"mkdir /var/www/{self.config['name']}/index.html", self.index_html)

    def create_copies(self):
            '''
            Cette fonction crée des copies des fichiers de configuration suivants : 
                /etc/apache2/sites-enabled/000-default.conf
            '''
            if self.ask("Souhaitez-vous créer des copies des fichiers '/etc/apache2/sites-enabled/000-default.conf' avant de commencer?"):
                commands = ["mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf.default",
                            "touch /etc/apache2/sites-enabled/000-default.conf"
                            ]
                for command in commands:
                    os.system(command)

    # installer apache2
    # le nom du site
    # fichier index.html par défaut ou alors 
    