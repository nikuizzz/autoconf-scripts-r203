import ipaddress
import subprocess
import os
from pprint import pprint

class Utils:
    @staticmethod
    def separator(reverse: bool = False):
        separator = ["", "-------------------------"]
        if reverse:
            for line in separator[::-1]:
                print(line)
        else:
            for line in separator:
                print(line)

    @staticmethod
    def ask(inputContent: str) -> bool:
        while True:
            myInput = str(input(f"{inputContent} ( O / n ) -> "))
            if myInput == "O":
                return True
            elif myInput == "n":
                return False
            elif myInput == "exit":
                exit()
            else:
                print("Saisie incorrecte.")
        

    @staticmethod
    def validate_ip_adress(address: str) -> bool:
        '''
        Permet de voir si le String passé en paramètre est une adresse IP valide.
        Renvoie True/False selon le résultat
        '''
        try:
            temp_ip = ipaddress.ip_address(address)
            return True
        except ValueError:
            return False
        
    @staticmethod
    def package_is_installed(package: str) -> bool:
        '''
        Permet de vérifier si un package ( passé en paramètre ) est installé sur le système Linux.
        Renvoie True/False selon le résultat
        '''
        dpkg = subprocess.Popen(['dpkg', '--get-selections'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', package], stdin=dpkg.stdout, stdout=subprocess.PIPE)
        result = list(grep.stdout)
        if len(result) == 1:
            return True
        else:
            return False
        
    @staticmethod
    def install_package(package: str):
        try:
            if(Utils.package_is_installed(package)):
                print(f"Le package '{package}' est déjà installé.")
            else:
                print(f"Le package '{package}' ne semble pas être installé sur votre système.")
                while True:
                    myInput = str(input("Souhaitez-vous l'installer? ( O / n ) -> "))
                    if myInput == "O":
                        try:
                            command = f"apt-get install -y {package}"
                            os.system(command)
                            break
                        except:
                            print(f"Une erreur est survenue lors de l'installation du package '{package}' ( Error 1 )")
                            break
                    elif myInput == "n":
                        break
                    else:
                        print("Saisie incorrecte. Reessayez.")
        except:
            print(f"Une erreur est survenue lors de l'installation du package '{package}' ( Error 2 )")

        
    @staticmethod
    def uninstall_package(package: str):
        if Utils.ask(f"Souhaitez-vous désinstaller le package {package}?"):
            if Utils.package_is_installed(package) is False:
                print(f"Le package '{package}' n'est pas installé.")
            else:
                try:
                    command = f"sudo apt-get purge -y --auto-remove {package}"
                    os.system(command)
                except:
                    print(f"Une erreur est survenue lors de la purge du package '{package}'")