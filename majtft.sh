echo "Sauvergarde des anciens fichiers tft dans old_version"
mv /opt/spotnik/spotnik2hmi/nextion/NX3224T024.tft /opt/spotnik/spotnik2hmi/old_version/NX3224T024`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX3224K024.tft /opt/spotnik/spotnik2hmi/old_version/NX3224K024`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX3224T028.tft /opt/spotnik/spotnik2hmi/old_version/NX3224T028`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX3224K028.tft /opt/spotnik/spotnik2hmi/old_version/NX3224K028`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX4024T032.tft /opt/spotnik/spotnik2hmi/old_version/NX4024T032`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX4024K032.tft /opt/spotnik/spotnik2hmi/old_version/NX4024K032`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX4832T035.tft /opt/spotnik/spotnik2hmi/old_version/NX4832K035`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX4832K035.tft /opt/spotnik/spotnik2hmi/old_version/NX4832K035`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX8048T050.tft /opt/spotnik/spotnik2hmi/old_version/NX8048K050`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX8048K050.tft /opt/spotnik/spotnik2hmi/old_version/NX8048K050`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX8048T070.tft /opt/spotnik/spotnik2hmi/old_version/NX8048K070`date +%d%m%Y`.tft
mv /opt/spotnik/spotnik2hmi/nextion/NX8048K070.tft /opt/spotnik/spotnik2hmi/old_version/NX8048K070`date +%d%m%Y`.tft


echo "telechargement des derniers fichiers tft"
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX3224T024.tft /opt/spotnik/spotnik2hmi/nextion/NX3224T024.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX3224K024.tft /opt/spotnik/spotnik2hmi/nextion/NX3224K024.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX3224T028.tft /opt/spotnik/spotnik2hmi/nextion/NX3224T028.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX3224K028.tft /opt/spotnik/spotnik2hmi/nextion/NX3224K028.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX4024T032.tft /opt/spotnik/spotnik2hmi/nextion/NX4024T032.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX4024K032.tft /opt/spotnik/spotnik2hmi/nextion/NX4024K032.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX4832T035.tft /opt/spotnik/spotnik2hmi/nextion/NX4832T035.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX4832K035.tft /opt/spotnik/spotnik2hmi/nextion/NX4832K035.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX8048T050.tft /opt/spotnik/spotnik2hmi/nextion/NX8048T050.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX8048K050.tft /opt/spotnik/spotnik2hmi/nextion/NX8048K050.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX8048T070.tft /opt/spotnik/spotnik2hmi/nextion/NX8048T070.tft
wget https://github.com/F8ASB/spotnik2hmi/blob/master/nextion/NX8048K070.tft /opt/spotnik/spotnik2hmi/nextion/NX8048K070.tft

