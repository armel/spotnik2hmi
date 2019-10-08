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
        'dtmf': '96#',
        'filter': '","RRF"]'
    },
    'fon': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/FON',
        'message': 'RESEAU FON',
        'dtmf': '97#',
        'filter': '","FON"]'
    },
    'tec': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/technique',
        'message': 'SALON TECHNIQUE',
        'dtmf': '98#',
        'filter': '","TECHNIQUE"]'
    },
    'int': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/international',
        'message': 'SALON INTER.',
        'dtmf': '99#',
        'filter': '","INTERNATIONAL"]'
    },
    'bav': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/bavardage',
        'message': 'SALON BAVARDAGE',
        'dtmf': '100#',
        'filter': '","BAVARDAGE"]'
    },
    'loc': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/local',
        'message': 'SALON LOCAL',
        'dtmf': '101#',
        'filter': '","LOCAL"]'
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
        'message': 'PERROQUET'
    }
}

versionDash = '3.01L'
wifistatut = 0

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
logo(versionDash)

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
print 'Maj version script : ' + versionDash
ecrire('boot.vascript.txt', str(versionDash))

# Affichage de la page Dashboard
print 'Page trafic ...'
page('trafic')

while True:
    # Gestion date et heure (en FR) 
    dashlist = ''
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
        ecrire('trafic.t0.txt',room_list[tn]['message'])
        if tn != 'default':
            url = room_list[tn]['url']
    else:
        ecrire('page200.t3.txt', 'Mode autonome')

    a.close()

    # Gestion status TRX

    print '>>>>>> AF' + url

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
        print data['transmitter']
        print data['receive']
    except:
        data = ''

    # Controle si page Dashboard RRF ou TEC

    if tn in room_list:
        if 'transmitter' in data:
            TxStation = data['transmitter']
        else:
            TxStation = ''
        if 'nodes' in data and len(data['nodes']) < 15:
            for n in ['RRF', 'TECHNIQUE', 'BAVARDAGE', 'INTERNATIONAL', 'LOCAL']:
                if n in data['nodes']:
                    data['nodes'].remove(n)
            dashlist = ''
            for n in data['nodes']:
                dashlist += n + ' '
            dashlist = dashlist.encode('utf-8')
        print TxStation
        print dashlist

    # Gestion des commandes serie reception du Nextion
    s = hmi_read_line()
    print 'Avant >>>>>>>', s
    s = ''.join(e for e in s if e.isalnum())
    print 'Apres >>>>>>>', s
    
    # Gestion des interactions Nextion

    if 'ouireboot' in s:
        print 'Reboot'
        page('boot')
        exit()
        #os.system('reboot')
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
        exit()
        #os.system('shutdown -h now')
    elif 'ouiquitecho' in s:
        print 'Oui quitte Echolink'
        dtmf('#')
        dtmf('96#')
        page('trafic')
    elif 'ouideconnectenode' in s:   
        print 'Deconnecte Node'
        page('echolink')
        dtmf('#')
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
        print 'New SSID: ' + newssid
        print 'New PASS: ' + newpass
        wifi(conf, newssid, newpass)
        page('wifi')
    elif 'maj' in s and 'ouimajwifi' not in s:
        print 'MAJ Wifi...'
        requete('get t0.txt')
        requete('get t1.txt')
        while True:
            t = hmi_read_line()
            if len(t) < 71:
                test= t.split(eof)
                newpass = test[0][1:]
                newssid = test[1][1:]
                print 'New SSID: ' + newssid
                print 'New PASS: ' + newpass
                wifistatut = 0
                break
        page('confirm')
        ecrire('confirm.t0.txt','CONFIRMER LA MAJ WIFI ?') 
    elif 'info' in s:
        print 'Detection bouton info'
        dtmf('*#')
    elif 'meteo' in s:
        print 'Detection bouton meteo'
        get_meteo()
    elif 'nodeqsy' in s:
        print 'Node choisi'
        print s[s.find('nodeqsy')+7:s.find('nodeqsy')+13] + '#'
        dtmf(s[s.find('nodeqsy')+7:s.find('nodeqsy')+13] + '#')
        page('echolink')
    elif 'trafic' in s:
        print 'Page trafic'
    elif 'dashboard' in s:
        print 'Page dashboard'
    elif 'menu' in s:
        print 'Page menu'
    elif 'pagewifi' in s:
        print 'Page wifi'
        Json='/etc/spotnik/config.json'
        if wifistatut == 0:
            with open(Json, 'r') as a:
                infojson = json.load(a)
                wifi_ssid = infojson['wifi_ssid']
                wifi_pass = infojson['wpa_key']
                print 'Envoi SSID actuel sur Nextion: ' + wifi_ssid
                print 'Envoi PASS actuel sur Nextion: ' + wifi_pass
                ecrire('wifi.t1.txt', str(wifi_ssid))
                ecrire('wifi.t0.txt', str(wifi_pass))
                wifistatut = 1  
    elif 'echolink' in s:
        print 'Page echolink'
    elif 'keypadnum' in s:
        print 'Page clavier numerique'
    elif 'connexionecho' in s:
        print 'Bouton connexion echolink'
    elif 'deconnectioncho' in s:
        print 'Bouton deconnexion echolink'
    elif 'regdim' in s:
        print 'Reglage DIM recu'
        rxdim = s[9:-3]
        print rdim
        rdmi= rxdim
    elif 'dmeteo' in s:
        print 'Bulletin Meteo'
        dtmf('*51#')
    elif 'qsyperroquet' in s:
        print 'QSY Perroquet'
        dtmf('95#')
    else:
        ecrire('page200.t3.txt', 'Mode autonome')

    # QSY Salon

    if s=='qsyinter':         # Fix me !!!
        s='qsyint'
    elif s=='qsytech':        # Fix me !!!
        s='qsytec'
    
    if s[-3:] not in room_list:
        ecrire('page200.t3.txt', 'Mode autonome')
    else:
        print 'QSY ' + room_list[s[-3:]]['message']
        print room_list[s[-3:]]['dtmf']
        dtmf(room_list[s[-3:]]['dtmf'])

    # Dashboard
    if s.find('listdash') == -1 and tn!='rrf' and tn!='fon':
        ecrire('page200.t3.txt', 'Mode autonome')
    else:
        #print 'Envoi dash'
        ecrire('trafic.g0.txt',dashlist)
