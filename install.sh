#!/bin/bash
 
# MAJ
echo "UPGRADE IN PROGRESS..."
sudo apt-get -y update
sudo apt-get -y dist-upgrade
sudo apt-get -y upgrade
echo "UPGRADE COMPLETED !"
 
echo "INSTALLATION DEPENDANCE PYTHON"
install -y gcc python-dev python-pip python-setuptools

echo "INSTALLATION COMPLETE !"

# PIP
echo "INSTALLATION PIP"
wget https://bootstrap.pypa.io/get-pip.py -O – | python
sudo pip install psutil
echo "INSTALLATION COMPLETE !"

echo "INSTALLATION scripts python"
git clone https://github.com/F8ASB/spotnik2hmi.git /opt/spotnik/

chmod +x /opt/spotnik/spotnik2hmi/spotnik2hmi.py

echo "INSTALLATION COMPLETE !"

echo "INSTALLATION UTILITAIRE METAR"
git clone https://github.com/python-metar/python-metar.git /opt/spotnik/spotnik2hmi/
echo "INSTALLATION COMPLETE !"

echo "Parametrage du port de l'ecran Nextion:"
echo "Sur quel port le branchez vous? ?"
echo
echo
echo "taper: ttyAMA (pour le port serie du raspberry GPIO pin 8 et 10)"
echo "taper: ttySS0 (pour le port UART J3 de l'OrangePi)"
echo "taper: USB00 (convertiseseur USB/SERIE sur le Raspberry Pi ou Orange Pi)"

read port

# Ecriture du script au demarage dans svxlin.rrf
if [ $port == "ttyAMA0" ]; then
echo "#demarrage script SPOTNIK2HMI" >> /etc/spotnik/restart.rrf
echo "python /opt/spotnik/spotnik2hmi.spotnik2hmi.py ttyAMA0 9600" >> /etc/spotnik/restart.rrf

elif [ $port == "USB0" ]; then
echo "#demarrage script SPOTNIK2HMI" >> /etc/spotnik/restart.rrf
echo "python /opt/spotnik/spotnik2hmi.spotnik2hmi.py ttyUSB0 9600" >> /etc/spotnik/restart.rrf

elif [ $port == "ttySS0" ]; then
echo "#demarrage script SPOTNIK2HMI" >> /etc/spotnik/restart.rrf
echo "python /opt/spotnik/spotnik2hmi.spotnik2hmi.py ttySS0 9600" >> /etc/spotnik/restart.rrf

else 
	echo "Le script n'est pas inscrit au demarrage"


echo "Voulez vous transferer le fichier .TFT sur ecran Nextion?"
echo 
echo "Regarder la reference a l'arriere de l'ecran et taper:"
echo
echo  "NX3224T024 (non disponible)"
echo  "NX4024T032 (non disponible)"
echo  "NX4832T035 (disponible)"
echo  "NX8048T050 (disponible)"
echo
echo  "NX3224K024 (non disponible)"
echo  "NX4024K032 (non disponible)"
echo  "NX4832K035 (disponible)"
echo  "NX8048K050 (disponible)"
echo
echo
echo "Il existe 2 sortes d'ecran, il y a la version standart avec un T ou la version Enhanced avec un K"
echo
echo "ATTENTION: Le protocole de transfert est simple et peut etrainer des erreurs, vous pouvez programmer"
echo "l'ecran en insérant directement une cart mini SD et le fichier TFT dessus"
echo


read installhmi


if [ $installhmi == "NX3224K024" ]; then
wget http://f8asb.com/spotnik2hmi/NX3224K024.tft
python nextion.py NX3224K024.tft '/dev/'+$port

elif [ $installhmi == "NX4024K032" ]; then
wget http://f8asb.com/spotnik2hmi/NX4024K032.tft
python nextion.py NX4024K032.tft '/dev/'+$port

elif [ $installhmi == "NX4832K035" ]; then
wget http://f8asb.com/spotnik2hmi/NX4832K035.tft
python nextion.py NX4832K035.tft '/dev/'+$port

elif [ $installhmi == "NX8048K050"" ]; then
wget http://f8asb.com/spotnik2hmi/NX8048K050.tft
python nextion.py NX8048K050.tft '/dev/'+$port

elif [ $installhmi == "NX3224T024" ]; then
wget http://f8asb.com/spotnik2hmi/NX3224T024.tft
python nextion.py NX3224T024.tft '/dev/'+$port

elif [ $installhmi == "NX4024T032" ]; then
wget http://f8asb.com/spotnik2hmi/NX4024T032.tft
python nextion.py NX4024T032.tft '/dev/'+$port

elif [ $installhmi == "NX4832T035" ]; then
wget http://f8asb.com/spotnik2hmi/NX4832T035.tft
python nextion.py NX4832T035.tft '/dev/'+$port

elif [ $installhmi == "NX8048T050"" ]; then
wget http://f8asb.com/spotnik2hmi/NX8048T050.tft
python nextion.py NX8048T050.tft '/dev/'+$port


else 
echo ""
echo "INSTALL TERMINEE AVEC SUCCES"
echo ""
echo " ENJOY ;) TEAM:F0DEI,F5SWB,F8ASB"
echo ""


