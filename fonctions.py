#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
# .-') _   ('-.  ) (`-.      .-') _                            .-') _      #        
#    ( OO ) )_(  OO)  ( OO ).   (  OO) )                          ( OO ) ) #
#,--./ ,--,'(,------.(_/.  \_)-./     '._ ,-.-')  .-'),-----. ,--./ ,--,'  #
#|   \ |  |\ |  .---' \  `.'  / |'--...__)|  |OO)( OO'  .-.  '|   \ |  |\  #
#|    \|  | )|  |      \     /\ '--.  .--'|  |  \/   |  | |  ||    \|  | ) #
#|  .     |/(|  '--.    \   \ |    |  |   |  |(_/\_) |  |\|  ||  .     |/  #
#|  |\    |  |  .--'   .'    \_)   |  |  ,|  |_.'  \ |  | |  ||  |\    |   #
#|  | \   |  |  `---. /  .'.  \    |  | (_|  |      `'  '-'  '|  | \   |   #
#`--'  `--'  `------''--'   '--'   `--'   `--'        `-----' `--'  `--'   #
#                                 TEAM: F0DEI,F5SWB,F8ASB      #    
############################################################################
#import echolink
import serial
import time
import os
import sys
import struct
import subprocess
import socket
import fcntl
import struct
from datetime import  *
import locale
import mmap
#partie dashboard
import urllib2
import ssl
#pour lecture fichier de config
import ConfigParser
#pour adresse ip
import socket
#pour CPU
import io
#pour json
import json
from subprocess import Popen, PIPE

# Variables:
eof = '\xff\xff\xff'
port = 0 
#Chemin fichier Json
Json='/etc/spotnik/config.json'
icao='/opt/spotnik/spotnik2hmi/datas/icao.cfg'
#routine ouverture fichier de config
svxconfig='/etc/spotnik/svxlink.cfg'
config = ConfigParser.RawConfigParser()
config.read(svxconfig)

# Fonction detection carte
def get_board():
    # Extract board revision from cpuinfo file
    revision = '0000'
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:8]=='Revision':
                length=len(line)
                revision = line[11:length-1]
        f.close()
    except:
        pass

    if revision == '0000':
        return 'Orange Pi'
    else:
        return 'Raspberry Pi' 

def portcom(portserie, vitesse):
    global port
    port = serial.Serial(port='/dev/' + portserie, baudrate=vitesse, timeout=1, writeTimeout=1)
    print 'Port serie: ' + portserie + ' Vitesse: ' + vitesse
    
# Reset HMI
def reset_hmi():
    global port
    print 'Reset HMI ...'
    reset ='rest' + eof  
    port.write(reset)

# Fonction requete du nextion
def requete(valeur):
    requetesend = str(valeur)+eof
    port.write(requetesend)

def hmi_read_line():
    global port
    rcv = port.readline()
    myString = str(rcv)
    return myString

# Fonction utilisation CPU
def get_cpu_usage():
    return str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))

# Fonction utilisation Memoire SD                 
def get_disk_usage():
    df_output = [s.split() for s in os.popen('df -h /').read().splitlines()]
    return(df_output[1][4])

# Fonction temperature
def get_cpu_temp():
    board = get_board()
    if board == 'Orange Pi':
        #temperature CPU
        f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
        t = f.readline ()
        cpu_temp = t[0:2]
    else: 
        #temperature CPU
        f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        t = f.readline ()
        cpu_temp = t[0:2]

    return cpu_temp

# Fonction de control d'extension au demarrage
def usage():
    program = os.path.basename(sys.argv[0])
    print ""    
    print"             "'\x1b[7;37;41m'"****ATTENTION****"+'\x1b[0m'
    print"" 
    print "Commande: python spotnik2hmi.py <port> <vitesse>"
    print "Ex: python spotnik2hmi.py ttyAMA0 9600"
    print ""
    sys.exit(1)

if len(sys.argv) > 2:
    print 'Ok'
else:
    usage()

# Fonction envoyer un code DTMF au system
def dtmf(code):
    b = open('/tmp/dtmf_uhf','a')
    b.write(code)
    print "code DTMF: " + code
    b.close()
    return 0

# Recuperation IP
def get_ip():
    # Adresse IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = (s.getsockname()[0])
    s.close()
    return ip

# Recuperation Frequence dans JSON
def get_frequency():
    # Recherche fréquence dans config.json
    with open(Json, 'r') as d:
        tmp= json.load(d)            
    return tmp['rx_qrg'] + ' Mhz'

# Recuperation indicatif dans Json       
def get_call_sign():
    # Recherche callsign dans config.json
    with open(Json, 'r') as d:
        tmp = json.load(d)
    return '(' + tmp['Departement'] + ') ' + tmp['callsign'] + ' ' + tmp['band_type']

#Fonction envoyer des commande console
def console(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    out, err = p.communicate()
    return (p.returncode, out, err)

#Fonction Wifi ECRITURE
def wifi(wifiid,wifipass):
    cfg = ConfigParser.ConfigParser()
    cfg.read(conf)
    cfg.set('connection', 'id', wifiid)
    cfg.set('wifi', 'ssid', wifiid)
    cfg.set('wifi-security', 'psk', wifipass)
    cfg.write(open(conf,'w'))

    #lecture de donnees JSON
    with open(Json, 'r') as f:
        config = json.load(f)
    #editer la donnee
        config['wifi_ssid'] = wifiid
        config['wpa_key'] = wifipass
    #write it back to the file
    with open(Json, 'w') as f:
        json.dump(config, f)
#Fonction ecriture texte sur Nextion ex: ecrire(t0.txt,"hello word")
def ecrire(champ,valeur):
    eof = '\xff\xff\xff'
    stringw = champ + '="' + valeur + '"' + eof
    port.write(stringw)

#Fonction appel de page
def page(nompage):
    eof = '\xff\xff\xff'
    appelpage = 'page ' + nompage + eof
    port.write(appelpage)
    print appelpage 

#Fonction recherche de nom de ville selon code ICAO
def get_city():
    # Lecture valeur icao dans config.json       
    with open(Json, 'r') as d:
        tmp = json.load(d)
    airport = tmp['airport_code']
        
    # Lecture ville dans fichier icao.cfg   

    icao2city = ConfigParser.RawConfigParser()
    config.read(icao)
    result_city = config.get('icao2city', airport)
    ecrire("meteo.t0.txt", result_city) 
    print "Aeroport de: " + result_city  

#Fonction Meteo Lecture des donnees Metar + envoi Nextion
def get_meteo():
    #recherche code IMAO dans config.json
    with open(Json, 'r') as b:
        afind= json.load(b)
        airport =afind['airport_code']
    #Info ville Aéroport
    print "Le code ICAO est: "+airport
    get_city()

    fichier = open("/tmp/meteo.txt", "w")
    fichier.write("[rapport]")
    fichier.close()

    result = console('/opt/spotnik/spotnik2hmi/python-metar/get_report.py '+ airport+ '>> /tmp/meteo.txt')
    print result
    #routine ouverture fichier de config
    config = ConfigParser.RawConfigParser()
    config.read('/tmp/meteo.txt')

    #recuperation indicatif et frequence
    pression = config.get('rapport', 'pressure')
    temperature = config.get('rapport', 'temperature')
    rose = config.get('rapport', 'dew point')
    buletin = config.get('rapport', 'time')
    buletin = config.get('rapport', 'time')
    heure = buletin.split(':')
    heure = heure[0][-2:] + ":"+heure[1]+ ":"+heure[2][:2]
    print(heure)
    print(pression[:-2])
    print(rose)
    print(temperature)
    ecrire("meteo.t1.txt",str(temperature))
    ecrire("meteo.t3.txt",str(heure))
    ecrire("meteo.t4.txt",str(rose))
    Pression = pression[:-2]+'hPa'
    ecrire("meteo.t2.txt",str(Pression))

def logo(Current_version):

    print'                                                 \x1b[7;30;47m'"oo" +'\x1b[0m'                                                
    print'\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m' 
    print'\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m' 
    print'\x1b[7;30;43m'+" -:::::- ::::::.  -::::-` -:::::: -:::. .:: -:: ::-   .::`     ::::-.     -::`  ::- ::::`  .::: -::`"+'\x1b[0m'
    print'\x1b[7;30;43m'+" //:---. ///.:// -//:-/// --://:- :////`:// /// ///  .//:      ---///-    ://.  //: ////- `//// ://."+'\x1b[0m'
    print'\x1b[7;30;43m'+" //:--.` ///`-// ://. ///   -//`  :////::// /// ///-///.        .///.     ://---//: /////`-//// ://."+'\x1b[0m'
    print'\x1b[7;30;43m'+" `.-:/// ///://: ://. ///   -//`  ://-///// /// ///-:///       -///:`     ://:--//: //::/://.// ://."+'\x1b[0m'
    print'\x1b[7;30;43m'+" ...-/// ///     ://:.///   -//`  ://.-//// /// ///  `///      ////-..    ://.  //: //:`///:`// ://."+'\x1b[0m'
    print'\x1b[7;30;43m'+" :::::-` ::-     `-::::-.   .::`  -::` -::: -:: ::-   ::-      :::::::    -::`  ::- ::- -::` :: -::`"+'\x1b[0m'
    print'\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m' 
    print'\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m' 
    print'                                                 \x1b[7;30;47m'"oo"+'\x1b[0m'                 
    print'\x1b[7;30;47m'"                Version :" +Current_version+"                    "           '\x1b[0m'+'\x1b[7;30;47m' + "          TEAM:"+ '\x1b[0m' +'\x1b[3;37;44m' + "/F0DEI"+ '\x1b[0m' +'\x1b[6;30;47m' + "/F5SWB"+ '\x1b[0m' + '\x1b[6;37;41m' + "/F8ASB"+ '\x1b[0m'
    print 
    print  
