#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Parametrage port serie

from fonctions import *
#import echolink

import serial
import sys
from datetime import  *
import time
from time import time,sleep

#pour lecture fichier de config
import ConfigParser, os
#pour adresse ip
import socket
#pour CPU
import io
#pour json
import json
#Pour ouverture nomenclature
import csv
import psutil
import os

#port=serial.Serial(port='/dev/'+sys.argv[1],baudrate=sys.argv[2],timeout=1, writeTimeout=1)
portcom(sys.argv[1],sys.argv[2])

#Variables
eof = "\xff\xff\xff"
today = datetime.now()
url = "http://rrf.f5nlg.ovh"
url2 = "http://rrf.f5nlg.ovh:82"
versionDash = "1.020119"
wifistatut = 0

#Reglage de luminosite
rdim = 10 #ecran sans reception signal
txdim = 80 # ecran avec reception station

#Chemins fichiers
svxconfig="/etc/spotnik/svxlink.cfg"
cheminversion= open("/etc/spotnik/version", "r")
version = cheminversion.read()
version = version.strip()
conf="/etc/NetworkManager/system-connections/SPOTNIK"
#icao="/opt/spotnik/spotnik2hmi/icao.cfg"
#Chemin log a suivre
svxlogfile = "/tmp/svxlink.log"   #SVXLink log file 

#Chemin fichier Json
#Json="/etc/spotnik/config.json"

#routine ouverture fichier de config
config = ConfigParser.RawConfigParser()
config.read(svxconfig)

#recuperation indicatif et frequence    
callsign = config.get('ReflectorLogic', 'CALLSIGN')
freq = config.get('LocationInfo', 'FREQUENCY')

#adresse IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip= (s.getsockname()[0])
s.close()

#temperature CPU
f = open("/sys/class/thermal/thermal_zone0/temp", "r")
t = f.readline ()
cputemp = t[0:2]+"." + t[3:4]

#Memoire SD libre
disk = psutil.disk_usage('/').percent
occupdisk = str(disk)+"%"

#Utilisation CPU
cpu = psutil.cpu_percent(interval=1)
chargecpu = str(cpu)+"%"


#Envoi des infos sur le Nextion

#print'                                                 \x1b[7;30;47m'"oo" +'\x1b[0m'                                                
#print'\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m' 
#print'\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m' 
#print'\x1b[7;30;43m'+" -:::::- ::::::.  -::::-` -:::::: -:::. .:: -:: ::-   .::`     ::::-.     -::`  ::- ::::`  .::: -::`"+'\x1b[0m'
#print'\x1b[7;30;43m'+" //:---. ///.:// -//:-/// --://:- :////`:// /// ///  .//:      ---///-    ://.  //: ////- `//// ://."+'\x1b[0m'
#print'\x1b[7;30;43m'+" //:--.` ///`-// ://. ///   -//`  :////::// /// ///-///.        .///.     ://---//: /////`-//// ://."+'\x1b[0m'
#print'\x1b[7;30;43m'+" `.-:/// ///://: ://. ///   -//`  ://-///// /// ///-:///       -///:`     ://:--//: //::/://.// ://."+'\x1b[0m'
#print'\x1b[7;30;43m'+" ...-/// ///     ://:.///   -//`  ://.-//// /// ///  `///      ////-..    ://.  //: //:`///:`// ://."+'\x1b[0m'
#print'\x1b[7;30;43m'+" :::::-` ::-     `-::::-.   .::`  -::` -::: -:: ::-   ::-      :::::::    -::`  ::- ::- -::` :: -::`"+'\x1b[0m'
#print'\x1b[7;30;47m'+" .oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo."+'\x1b[0m' 
#print'\x1b[7;30;47m'+" `::::::::::::::::::::::::::::::::::::::::::::::oooo::::::::::::::::::::::::::::::::::::::::::::::`"+'\x1b[0m' 
#print'                                                 \x1b[7;30;47m'"oo"+'\x1b[0m'                 
#print'\x1b[7;30;47m'"                Version :" +versionDash+"                    "           '\x1b[0m'+'\x1b[7;30;47m' + "          TEAM:"+ '\x1b[0m' +'\x1b[3;37;44m' + "/F0DEI"+ '\x1b[0m' +'\x1b[6;30;47m' + "/F5SWB"+ '\x1b[0m' + '\x1b[6;37;41m' + "/F8ASB"+ '\x1b[0m'
#print 
#print  
logo(versionDash)
print "Proc: "+(str(cpu))+"%   " + "CPU: "+cputemp+"°C" 
print "Station: "+callsign
print "Frequence: "+freq+" Mhz"
print "Spotnik: Version:"+version

#Reset ecran Nextion

resetHMI()

sleep(5);

#envoi indicatif
print "Maj Call ..."
ecrire("boot.va0.txt",callsign)
#Affichage de la page Dashboard
print "Page trafic ..."
page("trafic")

while 1:
#Gestion Date et heure (en FR)	
	today = datetime.now()
	locale.setlocale(locale.LC_TIME,'')	
	date = (today.strftime('%d-%m-%Y'))
        heure = (today.strftime('%H:%M'))
	heureS =(today.strftime('%H:%M:%S'))
	ecrire("trafic.t18.txt",date)
	ecrire("trafic.t8.txt",heureS)
	ecrire("trafic.t15.txt",heure) 	
#Definition et affichage link actif	
        a = open("/etc/spotnik/network","r")
        tn = a.read()

	if tn.find("rrf") == -1:
	
		ecrire("page200.t3.txt","Mode autonome")
	else:
	    
		ecrire("trafic.t0.txt","RESEAU RRF")
		url = "http://rrf.f5nlg.ovh"
		
	if tn.find("fon") == -1:
                
		ecrire("page200.t3.txt","Mode autonome")
	else:
		
		ecrire("trafic.t0.txt","RESEAU FON")	
	if tn.find("tec") == -1:
                
 		ecrire("page200.t3.txt","Mode autonome")
        else:
                
		ecrire("trafic.t0.txt","SALON TECHNIQUE")
		url = url2
		
	if tn.find("default") == -1:
                ecrire("page200.t3.txt","Mode autonome")
        	
	else:
		ecrire("trafic.t0.txt","PERROQUET")
	a.close()
#Gestion status TRX
	

# adresse sur le hotspot
# Salon TEC	url = "http://rrf.f5nlg.ovh:82"
# Salon	RRF  	url = "http://rrf.f5nlg.ovh"

#lecture du code source de la page

	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	the_page = response.read()
#controle si page Dashboard RRF ou TEC
	if tn.find("rrf") != -1:
		fincall= the_page.find ('</strong><!-- react-text: 18 --> <!-- /react-text --><img height="28" src="../static/receive.svg"')
		if fincall >0:
      	  		tramecall= (the_page[(fincall-30):fincall])
                        
 	    		call = tramecall.split('>')
      	  		print call[1]
			TxStation = call[1]
			setdim(txdim)
			
        	else:
			TxStation = ""	
			setdim(rdim)
	else:
		fincall= the_page.find ('</strong><img height="28" src="../static/receive.svg')	
		if fincall >0:
        		
        		tramecall= (the_page[(fincall-50):fincall])
        		
        		call = tramecall.split('>')
        		print call[1]
                	TxStation = call[1]
			setdim(txdim)
		else:
                       
  			TxStation = ""
       			dimsend ='dim='+str(rdim)+eof
                        setdim(rdim)
	
	if tn.find("el") != -1:
		i=0
		logfile = open(svxlogfile)
		loglines = follow(logfile)
		for line in loglines:
        	#print line
        		if "transmitter ON" in line:
                		print "TX ON"

        		elif "transmitter OFF" in line:
                		print "TX OFF"

        		elif "Shutting down application" in line:
                		print "SHUTTING DOWN SVX"
			elif "The squelch is OPEN"  in line:
                		print "SQUELCH OPEN"

        		elif "The squelch is CLOSED" in line:
                		print "SQUELCH CLOSED"
			elif "ECHO4: Frankfurt, Germany" in line:
                		print "Echolink Connexion Frankfurt"
			elif ">" in line:
                		print "info station"
                		call= line.split(">")
                		print call[1]
			elif StrRepeater+": Activating module " + StrEcholink  in line:
                		print StrEcholink+" module activated on "+StrRepeater
        		elif StrRepeater+": Deactivating module " + StrEcholink in line:
                		print StrEcholink+" module desactivated on "+StrRepeater
			elif StrSimplex+": Activating module " + StrEcholink  in line:
                		print StrEcholink+" module activated on "+StrSimplex
                	elif StrSimplex+": Deactivating module " + StrEcholink in line:
                		print StrEcholink+" module desactivated on "+StrSimplex
                	#elif "EchoLink QSO state changed to CONNECTED" in line:
            		#	ch =  line.split(':')
            		#	Last_Echolink_station = ch[0]
           # Echok_Station_conn = 1
            		#	print "ECHOLINK STATION CONNECTED"
            		#	print Last_Echolink_station= ch[0]

        		elif "EchoLink QSO state changed to BYE_RECEIVED" in line:
           # Echok_Station_conn = 0
            			print "ECHOLINK STATION DISCONNECTED"
       # port.write(heure)
	ecrire("trafic.t1.txt",TxStation)

#Gestion des commandes serie reception du Nextion
#	global port
#	rcv = port.readline()
#       value = (rcv)
#        myString = str(value)
	s = hmiReadline()
#	s = myString
	if len(s)<59 and len(s)>0:
		print s
		#print len(s)

#REBOOT
	if s.find("reboot")== -1:
		ecrire("page200.t3.txt","Mode autonome")
	else:
		print "Reboot command...."

#LECTURE DIM


#
#GESTION DU OUI DE LA PAGE CONFIRM
#


#OUIREBOOT#
        if s.find("ouireboot")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
		print "REBOOT"
                page("boot")
                os.system('reboot')
#OUIRESTART#
        if s.find("ouirestart")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "REDEMARRAGE"
                os.system('bash /etc/spotnik/restart.rrf')
                exit()
#OUIARRET#
        if s.find("ouiarret")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "ARRET DU SYSTEM"
                page("boot")
                os.system('shutdown -h now')
#OUIWIFI
	if s.find("ouimajwifi")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                wifi(newssid,newpass)
                page("wifi")
#OUIQUITTERECOLINK#
        if s.find("ouiquitecho")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "OUI QUITTE ECHOLINK"
                dtmf("#")
		page("trafic")
		dtmf("96#")
                
#OUICONNEXIONNODE#
#        if s.find("ouiconnectenode")== -1:
#                ecrire("page200.t3.txt","Mode autonome")
#        else:
#                print "QSY SUR LE NODE"
#                numpadvalue ='get keypadnum.va0.txt' +eof
#                port.write(numpadvalue)
#		page("echolink")

#OUIDECONNECTIONNODE#
        if s.find("ouideconnectenode")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "DECONNECTE NODE"
                page("echolink")
                dtmf("#")
                                                                              
#STOP		
	
	if s.find("shutdown")== -1:               
		ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Shutdown command...."		
		page("confirm")
		ecrire("confirm.t0.txt","CONFIRMER UN ARRET TOTAL?")			
#RESTART
        if s.find("restart")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Restart command...."
                page("confirm")
                ecrire("confirm.t0.txt","CONFIRMER LE REDEMARRAGE LOGICIEL?")

#REBOOT
        if s.find("reboot")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Reboot command...."
		page("confirm")
                ecrire("confirm.t0.txt","CONFIRMER LE REBOOT GENERAL?")

#MAJWIFI
        if s.find("maj")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "MAJ Wifi...."
		requete ='get t0.txt' +eof
		port.write(requete)
		requete2 ='get t1.txt' +eof
                port.write(requete2)
		while 1:
			rcv = port.readline()
        		value = (rcv)
        		myString = str(value)
        		s = myString        		
       			if len(s)<71:		
				test= s.split("p")
        			newpass= test[1][:-3]
				newssid= test[2][:-3]		
				print "New SSID: "+newssid
				print "New PASS: "+newpass			
				wifistatut = 0
				break
                
               	page("confirm")
		ecrire("confirm.t0.txt","CONFIRMER LA MAJ WIFI?")		
#INFO#	
	if s.find("info")== -1:
                ecrire("page200.t3.txt","Mode autonome")
	else:
		print "Detection bouton info"
		cput = '"'+cputemp+' C'+'"' 
		ecrire("info.t14.txt",cputemp)
		print "Station: "+callsign
		Freq = freq+ ' Mhz'
		print "Frequence: "+freq
		ecrire("info.t15.txt",Freq)
		print "Spotnik: "+version
		ecrire("info.t10.txt",version)
		print "Script Version: "+versionDash
		ecrire("info.t16.txt",versionDash)
		print "Occupation disk: "+(occupdisk)
		ecrire("info.t13.txt",occupdisk)
		print "IP: "+ip
		ecrire("info.t0.txt",ip)
		print "occupation systeme: "+(chargecpu)
                ecrire("info.t12.txt",chargecpu)

#METEO#
	if s.find("meteo")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                
		print "Detection bouton meteo"
                #METEO
		get_meteo()
#NODE#
        if s.find("nodeqsy")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:

                print "Node choisi"
		print s[s.find("nodeqsy")+7:s.find("nodeqsy")+13]+"#"
                dtmf(s[s.find("nodeqsy")+7:s.find("nodeqsy")+13]+"#")
		page("echolink")							
#TRAFIC#		
	if s.find("trafic")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
		print "Page trafic"
		
#DASHBOARD#
	if s.find("dashboard")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Page dashboard"
		
#MENU#
        if s.find("menu")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Page menu"
#WIFI#
        if s.find("wifi")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Page wifi"
                Json="/etc/spotnik/config.json"				
               	if wifistatut == 0:			                		
			with open(Json, 'r') as a:
                		infojson = json.load(a)
				wifi_ssid = infojson['wifi_ssid']
				wifi_pass = infojson['wpa_key']
				print "Envoi SSID actuel sur Nextion: "+wifi_ssid
				print "Envoi PASS actuel sur Nextion: "+wifi_pass
 				ecrire("wifi.t1.txt",str(wifi_ssid))
				ecrire("wifi.t0.txt",str(wifi_pass))
				wifistatut = 1

	#Gestion des commande DTMF
# 	b = open("/tmp/svxlink_dtmf_ctrl_pty","a")
# 	s = myString
#	b.write(myString)
# 	b.close()	

#ECHOLINK#
        if s.find("echolink")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Page echolink"
#Numkaypad#
        if s.find("keypadnum")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Page clavier numerique"
#Quitte Echolink#
#        if s.find("quittecho")== -1:
#                ecrire("page200.t3.txt","Mode autonome")
#        else:
#                print "Bouton quitter echolink"
#		page("confirm")
#                ecrire("confirm.t0.txt","QUITTER ECHOLINK?")	
	
#Connect Echolink#
        if s.find("connexionecho")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Bouton connexion echolink"
		
		
#Deconnect Echolink#
        if s.find("deconnectioncho")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Bouton deconnexion echolink"
                

#Reglage DIM#
        if s.find("regdim")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "Reglage DIM recu"
                rxdim = s[9:-3]
		print rdim
		rdmi= rxdim
		
#QSYSALONTECH#
        if s.find("qsytech")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "QSY SALON TECH"
                dtmf("98#")
#QSYSALONRRF#
        if s.find("qsyrrf")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "QSY SALON RRF"
                dtmf("96#")
#QSYFON#
        if s.find("qsyfon")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "QSY FON"
                dtmf("97#")
#QSYECHOLINK#
        if s.find("qsyecho")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "QSY ECHOLINK"
                dtmf("102#")
#DONNMETEO#
        if s.find("dmeteo")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "BULETIN METEO"
                dtmf("*51#")
#PERROQUET#
        if s.find("parrot")== -1:
                ecrire("page200.t3.txt","Mode autonome")
        else:
                print "PERROQUET"
                print "NON DISPONIBLE"
		#dtmf("")


