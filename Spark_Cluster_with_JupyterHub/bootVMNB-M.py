# -*- coding: utf8 -*-
#!/usr/bin/python
import os, time, sys
from novaclient.v1_1 import client as nvclient

# vérification de la présence du paramètre (@IP de PunchPlatform)
if len(sys.argv) != 3:
  print("Syntax: %s vm-name userdata-file\n") % sys.argv[0]
  sys.exit(1)
else:
  vm_name = sys.argv[1]
  userdata_file = sys.argv[2]

# connexion aux services de Cloud OMC / IMA (nova)
nova = nvclient.Client(username=os.environ['OS_USERNAME'],
  project_id=os.environ['OS_TENANT_NAME'],
  api_key=os.environ['OS_PASSWORD'],
  auth_url=os.environ['OS_AUTH_URL'],
  insecure=True)

# réseau privé sur Cloud OMC / IMA
net_id="67a3e2c9-424a-463a-8a73-cccde3de4443"
nics = [{"net-id": net_id, "v4-fixed-ip": ''}]

# image de la VM (Ubuntu 14.04 LTS sous KVM)
image = nova.images.find(id="4fef4b01-31eb-4cc1-9960-d1dca922e546")

# (petite) VM avec 4Go de RAM
flavor = nova.flavors.find(name="t1.standard.medium-1")

# descripteur du fichier des commandes shell à passer au boot de la VM
ufile = open(userdata_file, 'r')

# nom de la VM
name = vm_name

# lancement de la VM 
instance = nova.servers.create(name=name, 
  image=image, 
  flavor=flavor, 
  nics=nics,
  userdata=ufile,
  key_name="KP-OMC-01")

status = instance.status

# attente relative au boot de la VM
sec = 0
while status != 'ACTIVE':
    sec = sec + 1 
    time.sleep(5)
    instance = nova.servers.get(instance.id)
    status = instance.status
    sys.stdout.write(".")
    sys.stdout.flush()

print ""
print "status: %s (boot in %d sec)" % (status, sec * 5)

# récupération d'une adresse IP flottante et association à la VM
floating_ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)
instance.add_floating_ip(floating_ip)
print "IP Internet = %s\n" % floating_ip.ip

ufile.close()
sys.exit(0)
