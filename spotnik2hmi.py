#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Parametrage port serie

from fonctions import *
#import echolink

import serial
import sys
import datetime
import time
import requests
#pour lecture fichier de config
import ConfigParser, os
#pour adresse ip
import socket
#pour json
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

versionDash = '3.00L'
wifistatut = 0

a = open('/etc/spotnik/network','r')
tn = a.read().strip()

if tn in ['default', 'sat']:
    os.system('echo "rrf" > /etc/spotnik/network')
    os.system('/etc/spotnik/restart')
    print 'NETWORK CHANGE'
else: 
    print 'NETWORK OK'
        
#Reglage de luminosite
rdim = 10   #ecran sans reception signal
txdim = 80  #ecran avec reception station

#Chemins fichiers
svxconfig='/etc/spotnik/svxlink.cfg'
cheminversion= open('/etc/spotnik/version', 'r')
version = cheminversion.read()
version = version.strip()
conf='/etc/NetworkManager/system-connections/SPOTNIK'

#Chemin log a suivre
svxlogfile = '/tmp/svxlink.log'   #SVXLink log file 

#routine ouverture fichier de config
config = ConfigParser.RawConfigParser()
config.read(svxconfig)

#recuperation indicatif et frequence    
call_sign = get_call_sign()
frequency = get_frequency()

#adresse IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
ip= (s.getsockname()[0])
s.close()

# Utilisation Memoire SD
disk_usage = get_disk_usage()

# Utilisation CPU
cpu_usage = get_cpu_usage()

# Detection carte
board = get_board()

# Temperature
cpu_temp = get_cpu_temp()

#Envoi des infos 
  
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
        url = room_list[tn]['url']
    else:
        ecrire('page200.t3.txt','Mode autonome')

    a.close()

    # Gestion status TRX

    # Request HTTP datas
    try:
        r = requests.get(url, verify=False, timeout=10)
        page_web = r.content
    except requests.exceptions.ConnectionError as errc:
        print ('Error Connecting:', errc)
        ecrire('trafic.t1.txt','DASH HS')
    except requests.exceptions.Timeout as errt:
        print ('Timeout Error:', errt)
        ecrire('trafic.t1.txt','DASH HS')
	
    # Controle si page Dashboard RRF ou TEC

    if tn in room_list:
        fincall= page_web.find ('"transmitter":"')
        if tn not in ['rrf', 'fon', 'sat']:
            dashdebut= page_web.find ('"nodes":[')
            dashfin= page_web.find (room_list[tn]['filter'])
        
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
            call = tramecall.split('"')
            print call[3]
            if tn not in ['rrf', 'fon', 'sat']:
                tramedash= (page_web[(dashdebut+10):(dashfin)])
                dashlist= tramedash.replace('"','')
                print 'dashlist:'+dashlist
            TxStation = call[3]
        else:
            TxStation = ''

    # Gestion des commandes serie reception du Nextion
    s = hmi_read_line()

    if len(s)<59 and len(s)>0:
        print s
    s=''.join(e for e in s if e.isalnum())
    print 'Armel' + s

    #REBOOT
    if s.find('reboot')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Reboot command....'

    #
    #GESTION DU OUI DE LA PAGE CONFIRM
    #

    #OUIREBOOT#
    if s.find('ouireboot')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'REBOOT'
        page('boot')
        os.system('reboot')

#OUIRESTART#
    if s.find('ouiredem')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'REDEMARRAGE'
        dtmf('96#')
        page('trafic')
                
#OUIARRET#
    if s.find('ouiarret')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'ARRET DU SYSTEM'
        page('arret')
        os.system('shutdown -h now')

#OUIWIFI
    if s.find('ouimajwifi')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        wifi(newssid,newpass)
        page('wifi')

#OUIQUITTERECOLINK#
    if s.find('ouiquitecho')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'OUI QUITTE ECHOLINK'
        dtmf('#')
        page('trafic')
        dtmf('96#')
                
#OUIDECONNECTIONNODE#
    if s.find('ouideconnectenode')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'DECONNECTE NODE'
        page('echolink')
        dtmf('#')
#
#Gestion commande du Nextion
#
                                                                              
#STOP
    if s.find('shutdown')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Shutdown command....'
        page('confirm')
        ecrire('confirm.t0.txt','CONFIRMER UN ARRET TOTAL ?')			
#RESTART
    if s.find('restart')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Restart command....'
        page('confirm')
        ecrire('confirm.t0.txt','CONFIRMER LE REDEMARRAGE LOGICIEL ?')

#REBOOT
    if s.find('reboot')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Reboot command....'
        page('confirm')
        ecrire('confirm.t0.txt','CONFIRMER LE REBOOT GENERAL ?')

#MAJWIFI
    if s.find('maj')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'MAJ Wifi....'
        requete('get t0.txt')
        requete('get t1.txt')

        while True:
            s = hmi_readl_ine()
            if len(s)<71:
                test= s.split('p')
                newpass= test[1][:-3]
                newssid= test[2][:-3]
                print 'New SSID: '+newssid
                print 'New PASS: '+newpass
                wifistatut = 0
                break
        page('confirm')
        ecrire('confirm.t0.txt','CONFIRMER LA MAJ WIFI ?')		
#INFO#	
    if s.find('info')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Detection bouton info'
        dtmf('*#')
#METEO#
    if s.find('meteo')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Detection bouton meteo'
        #METEO
        get_meteo()
#NODE#
    if s.find('nodeqsy')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Node choisi'
        print s[s.find('nodeqsy')+7:s.find('nodeqsy')+13]+'#'
        dtmf(s[s.find('nodeqsy')+7:s.find('nodeqsy')+13]+'#')
        page('echolink')							
#TRAFIC#		
    if s.find('trafic')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Page trafic'
		
#DASHBOARD#
    if s.find('dashboard')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Page dashboard'
		
#MENU#
    if s.find('menu')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Page menu'
#WIFI#
    if s.find('wifi')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
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

#ECHOLINK#
    if s.find('echolink')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Page echolink'
#Numkaypad#
    if s.find('keypadnum')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Page clavier numerique'
	
#Connect Echolink#
    if s.find('connexionecho')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Bouton connexion echolink'
		
		
#Deconnect Echolink#
    if s.find('deconnectioncho')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Bouton deconnexion echolink'
                

#Reglage DIM#
    if s.find('regdim')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'Reglage DIM recu'
        rxdim = s[9:-3]
        print rdim
        rdmi= rxdim

#QSYSALON

    s=''.join(e for e in s if e.isalnum())

    if s=='qsyinter':         # Fix me !!!
        s='qsyint'
    elif s=='qsytech':        # Fix me !!!
        s='qsytec'
    print '>>>>>>>' + s, s[-3:]
    
    if s[-3:] not in room_list:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'QSY ' + room_list[s[-3:]]['message']
        print room_list[s[-3:]]['dtmf']
        dtmf(room_list[s[-3:]]['dtmf'])

#DONNMETEO#
    if s.find('dmeteo')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'BULETIN METEO'
        dtmf('*51#')
#PERROQUET
    if s.find('qsyperroquet')== -1:
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'QSY PERROQUET'
        dtmf('95#')
#DASHBOARD#
    if s.find('listdash')== -1 and tn!='rrf' and tn!='fon':
        ecrire('page200.t3.txt','Mode autonome')
    else:
        print 'ENVOI DASH'
        ecrire('trafic.g0.txt',dashlist)
