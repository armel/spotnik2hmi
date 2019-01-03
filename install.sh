#!/bin/bash
whiptail --title "INFORMATION:" --msgbox "Ce script considère que vous partez d’une image disponible par F5NLG du Spotnik 1.9 et fonctionnelle sur Raspberry ou Orange Pi.Il permet d’ajouter un écran Nextion à la distribution. Plus d'informations sur http://blog.f8asb.com/spotnik2hmi.                                                                                         Team F0DEI/F5SWB/F8ASB" 15 60


#!/bin/bash
INSTALL=$(whiptail --title "Choisir votre installation" --radiolist \
"Que voulez vous installer?" 15 60 4 \
"SPOTNIK2HMI" "Gestion Nextion avec Spotnik " ON \
"NEXTION" "Programmation ecran Nextion " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?

if [ $exitstatus = 0 ]; then
    echo "Installation de :" $INSTALL

else
    echo "Vous avez annulé"
fi

if [ $INSTALL = "SPOTNIK2HMI" ]; then

# MAJ
echo "UPGRADE IN PROGRESS..."
#apt-get -y update
#apt-get -y dist-upgrade
#apt-get -y upgrade
echo "UPGRADE COMPLETED !"
 
echo "INSTALLATION DEPENDANCE PYTHON"
apt-get -y install gcc python-dev python-pip python-setuptools

echo "INSTALLATION COMPLETE !"

# PIP
echo "INSTALLATION PIP"
wget https://bootstrap.pypa.io/get-pip.py -O – | python
pip install psutil
echo "INSTALLATION COMPLETE !"

echo "INSTALLATION scripts python"
git clone https://github.com/F8ASB/spotnik2hmi.git /opt/spotnik/spotnik2hmi/

chmod +x /opt/spotnik/spotnik2hmi/spotnik2hmi.py

echo "INSTALLATION COMPLETE !"

echo "INSTALLATION UTILITAIRE METAR"
git clone https://github.com/python-metar/python-metar.git /opt/spotnik/spotnik2hmi/python-metar/
echo "INSTALLATION COMPLETE !"

PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttySS0" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)

exitstatus=$?
if [ $exitstatus = 0 ]; then

echo 'python /opt/spotnik/spotnik2hmi.spotnik2hmi.py' $PORT '9600' >> /etc/rc.local
else
    echo "Vous avez annulé"
fi
exit

else

PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttySS0" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Port du Nextion :" $PORT
else
    echo "Vous avez annulé"
fi

ECRAN=$(whiptail --title "Choix type d'ecran NEXTION" --radiolist \
"Quel Type d'ecran ?" 15 60 4 \
"NX3224K024.tft" "Ecran 2,4 Enhanced (non dispo)" OFF \
"NX3224T024.tft" "Ecran 2,4 Basic (non dipo)" OFF \
"NX4832K035.tft" "Ecran 3,5 Enhanced" OFF \
"NX4832T035.tft" "Ecran 3,5 Basic" ON \
"NX8048K050.tft" "Ecran 5,0 Enhanced" OFF \
"NX8048T050.tft" "Ecran 5,0 Basic" OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Type d'écran :" $ECRAN
python /opt/spotnik/spotnik2hmi/nextion/nextion.py '/opt/spotnik/spotnik2hmi/nextion/'$ECRAN '/dev/'$PORT

else
    echo "Vous avez annulé"
fi
fi


echo ""
echo "INSTALL TERMINEE AVEC SUCCES"
echo ""
echo " ENJOY ;) TEAM:F0DEI,F5SWB,F8ASB"
echo ""

