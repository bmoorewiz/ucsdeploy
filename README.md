# ucsdeploy

This file will walk you through deploying a UCS installtion mostly used with vmware. 

You can either use a file to keep the variables, or the script will ask you for them. 

This will create UUID, MAC, WWPn, WWNN pools and a service profile with all attached updating profiles. It can also create vlans with names and assign all of them
to the NIC interfaces. 

#install the UCS SDK
pip install ucsmsdk
#install xlrd
pip install xlrd

#The script assumes you are using admin as the login, if that is different, you will need to change the script to accomodate. First variable is the IP of the UCS cluster and the 2nd variable is the admin password. 
python ucsinstall.py 1.1.1.1 password
