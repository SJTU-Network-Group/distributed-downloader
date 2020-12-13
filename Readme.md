![image](https://github.com/SJTU-Network-Group/distributed-downloader/blob/master/ReadmeFig/logo.png)
# SJTU-CS339-Teamwork-Distributed-Downloader
This repository contains the code of our CS339 Computer Network's team project Distributed Downloader. 
Here we will give you a simple example to show you how to use the repository to accelerate your download through a distributed way. 
The design principle and detailed architecture you can refer to our paper.

## How to use
First of all, you should satisfy the following requirement:
> python >= 3.6

and then you can install other dependency by running:
> pip3 install -r requirements.txt

and to run server, client and manager instance properly, you need to follow our examples *client/config/client_config_example.yml*, 
*server/config/server_config_example.yml* and *manager/config/manager_config_example.yml* to create your own config files *client_config.yml*, 
*server_config.yml* and *manager_config.yml* under the same directory.

Second, you must start a manager instance on the manager machine by running:
> python manager_cli,py

After you start the manager instance, you can see manager's ipv4 address in the terminal, change the **MANAGER_ADDR_IPV4** in
*client/config/client_config.yml* on the client machine and *server/config/server_config.yml* on the server machines to make sure
that they can connect with proper manager.

Third, start some server instances on server machines by running:
> python server_cli.py

Client will download faster if you start more server instances here.

Last, start a client instance and assign a download URL to it by running:
> python client_cli.py *$given URL$*

Now you can enjoy your fast download!