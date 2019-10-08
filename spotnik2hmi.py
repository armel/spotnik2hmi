#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Parametrage port serie

from fonctions import *

import serial
import sys
import datetime
import time
import requests
import ConfigParser, os
import json
import os

portcom(sys.argv[1],sys.argv[2])

#Variables
eof = '\xff\xff\xff'
url = ''

room_list = {
    'rrf': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/RRF',
        'message': 'RESEAU RRF',
        'dtmf': '96#'
    },
    'fon': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/FON',
        'message': 'RESEAU FON',
        'dtmf': '97#'
    },
    'tec': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/technique',
        'message': 'SALON TECHNIQUE',
        'dtmf': '98#'
    },
    'int': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/international',
        'message': 'SALON INTER.',
        'dtmf': '99#'
    },
    'bav': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/bavardage',
        'message': 'SALON BAVARDAGE',
        'dtmf': '100#'
    },
    'loc': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/local',
        'message': 'SALON LOCAL',
        'dtmf': '101#'
    },
    'sat': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/satellite',
        'message': 'SALON SAT',
        'dtmf': '102#'
    },
    'reg': {
        'url': '',
        'message': 'SALON REGIONAL',
        'dtmf': '104#'
    },
    'default': {
        'url': '',
        'message': 'PERROQUET',
        'dtmf': '95#'
    }
}

version_dash = '3.01L'
wifi_statut = 0

a = open('/etc/spotnik/network','r')
tn = a.read().strip()

if tn in ['default', 'sat']:
    os.system('echo "rrf" > /etc/spotnik/network')
    os.system('/etc/spotnik/restart')
    print 'Network Change'
else: 
    print 'Network Ok'
        
# Reglage de luminosite
rdim = 10   #ecran sans reception signal
txdim = 80  #ecran avec reception station

# Chemins fichiers
svxconfig = '/etc/spotnik/svxlink.cfg'
cheminversion = open('/etc/spotnik/version', 'r')
version = cheminversion.read()
version = version.strip()
conf = '/etc/NetworkManager/system-connections/SPOTNIK'

# Chemin log a suivre
svxlogfile = '/tmp/svxlink.log'   #SVXLink log file 

# Routine ouverture fichier de config
config = ConfigParser.RawConfigParser()
config.read(svxconfig)

# Recuperation indicatif, frequence
call_sign = get_call_sign()
frequency = get_frequency()

# Utilisation memoire SD, charge CPU, temperature CPU, IP et type de carte
disk_usage = get_disk_usage()
cpu_usage = get_cpu_usage()
cpu_temp = get_cpu_temp()
ip = get_ip()
board = get_board()

# Envoi des infos 
logo(version_dash)

print 'Carte : ' + board
print 'Proc : ' + cpu_usage + '%'
print 'CPU : ' + cpu_temp + '°C' 
print 'Station : ' + call_sign
print 'Frequence : ' + frequency
print 'Spotnik Version : ' + version

#Reset ecran Nextion

reset_hmi()

time.sleep(5);

#envoi information systeme
print 'Maj Call : ' + call_sign
ecrire('boot.va0.txt', str(call_sign))
print 'Maj info disk : ' + disk_usage
ecrire('boot.vasd.txt', str(disk_usage))
print 'Maj info freq : ' + frequency
ecrire('boot.vafreq.txt', str(frequency))
print 'Maj ip : ' + ip
ecrire('boot.vaip.txt', str(ip))
print 'Maj version : '+ version
ecrire('boot.vaverspotnik.txt', str(version))
print 'Maj version script : ' + version_dash
ecrire('boot.vascript.txt', str(version_dash))

# Affichage de la page Dashboard
print 'Page trafic ...'
page('trafic')
whereis = 'trafic'

while True:
    #
    # Lecture des évenements en provenance du Nextion
    #

    s = hmi_read_line()
    print 'Avant >>>>>>>', s

    s = ''.join(e for e in s if e.isalnum())

    if s != '':
        if s == 'qsyinter':         # Fix me !!!
            s = 'qsyint'
        elif s == 'qsytech':        # Fix me !!!
            s = 'qsytec'
        elif s == 'qsyperroquet':   # Fix me !!!
            s = 'qsydefault'

        if 'trafic' in s:
            whereis = 'trafic'
        else:
            whereis = 'eleswhere'

    print 'Apres >>>>>>>', s, s[-3:]
    print 'Whereis', whereis

    #
    # Si page trafic
    #

    if whereis == 'trafic':
        # Gestion date et heure (en FR) 
        node_list = ''
        today = datetime.datetime.now()
        locale.setlocale(locale.LC_TIME,'')
        ecrire('trafic.t18.txt', today.strftime('%d-%m-%Y'))
        ecrire('trafic.t8.txt', today.strftime('%H:%M:%S'))
        ecrire('trafic.V_heure.txt', today.strftime('%H:%M'))
        requete('vis p9,0')
        ecrire('trafic.t15.txt', today.strftime('%H:%M'))

        # Definition et affichage link actif    
        a = open('/etc/spotnik/network','r')
        tn = a.read().strip()

        if tn in room_list:
            ecrire('trafic.t0.txt', room_list[tn]['message'])
            if tn != 'default':
                url = room_list[tn]['url']

        a.close()

        # Request HTTP datas
        try:
            r = requests.get(url, verify=False, timeout=10)
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
            ecrire('trafic.t1.txt','DASH HS')
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)
            ecrire('trafic.t1.txt','DASH HS')
        
        try:
            data = r.json()
        except:
            data = ''

        # Controle si page Dashboard RRF ou TEC

        if tn in room_list:
            node_active = ''
            node_list = ''
            if 'transmitter' in data:
                node_active = data['transmitter']
                node_active = node_active.encode('utf-8')
            else:
                node_active = ''
            if 'nodes' in data and len(data['nodes']) < 16:
                for n in ['RRF', 'TECHNIQUE', 'BAVARDAGE', 'INTERNATIONAL', 'LOCAL']:
                    if n in data['nodes']:
                        data['nodes'].remove(n)
                for n in data['nodes']:
                    node_list += n + ' '
                node_list = node_list.encode('utf-8')
            ecrire("trafic.t1.txt",node_active)
            if node_active != '':
                print node_active
                command('dim', str(100))
            else:
                command('dim', str(5))
            if node_list != '':
                print node_list
                ecrire("trafic.g0.txt",node_list)
    #
    # Sinon gestion des interactions Nextion
    #

    else:
        if 'ouireboot' in s:
            print 'Reboot'
            page('boot')
            os.system('reboot')
        elif 'reboot' in s:
            print 'Reboot command....'
            page('confirm')
            ecrire('confirm.t0.txt','CONFIRMER LE REBOOT GENERAL ?')
        elif 'ouiredem' in s:
            print 'Redemarrage'
            dtmf('96#')
            page('trafic')
        elif 'ouiarret' in s:
            print 'Arret du system'
            page('arret')
            os.system('shutdown -h now')
        elif 'shutdown' in s:
            print 'Shutdown command...'
            page('confirm')
            ecrire('confirm.t0.txt','CONFIRMER UN ARRET TOTAL ?')           
        elif 'restart' in s:       
            print 'Restart command...'
            page('confirm')
            ecrire('confirm.t0.txt','CONFIRMER LE REDEMARRAGE LOGICIEL ?')
        elif 'ouimajwifi' in s:
            print 'Wifi Update'
            print 'New SSID: ' + new_ssid
            print 'New PASS: ' + new_pass
            wifi(conf, new_ssid, new_pass)
            page('wifi')
        elif 'maj' in s and 'ouimajwifi' not in s:
            print 'MAJ Wifi...'
            requete('get t0.txt')
            requete('get t1.txt')
            while True:
                t = hmi_read_line()
                if len(t) < 71:
                    test = t.split(eof)
                    new_pass = test[0][1:]
                    new_ssid = test[1][1:]
                    print 'New SSID: ' + new_ssid
                    print 'New PASS: ' + new_pass
                    wifi_statut = 0
                    break
            page('confirm')
            ecrire('confirm.t0.txt','CONFIRMER LA MAJ WIFI ?') 
        elif 'info' in s:
            print 'Detection bouton info'
            dtmf('*#')
        elif 'meteo' in s:
            print 'Detection bouton meteo'
            get_meteo()
        elif 'trafic' in s:
            print 'Page trafic'
        elif 'menu' in s:
            print 'Page menu'
        elif 'pagewifi' in s:
            print 'Page wifi'
            Json='/etc/spotnik/config.json'
            if wifi_statut == 0:
                with open(Json, 'r') as a:
                    info_json = json.load(a)
                    wifi_ssid = info_json['wifi_ssid']
                    wifi_pass = info_json['wpa_key']
                    print 'Envoi SSID actuel sur Nextion: ' + wifi_ssid
                    print 'Envoi PASS actuel sur Nextion: ' + wifi_pass
                    ecrire('wifi.t1.txt', str(wifi_ssid))
                    ecrire('wifi.t0.txt', str(wifi_pass))
                    wifi_statut = 1  
        elif 'regdim' in s:
            print 'Reglage DIM recu'
        elif s[3:] in room_list:
            print 'QSY ' + room_list[s[3:]]['message'] + ' ' + room_list[s[3:]]['dtmf']
            dtmf(room_list[s[3:]]['dtmf'])
