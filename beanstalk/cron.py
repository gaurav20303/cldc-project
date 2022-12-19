import os
import time
import requests
from cloudProject import settings

DIGITALOCEAN_TOKEN = settings.DIGITALOCEAN_TOKEN

headers = {
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
    'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
}

def scale_up():
    load_balancer = '83ef52cc-7328-4d01-81c7-9b5b82a63cc5'

    response1 = requests.get(
        'https://api.digitalocean.com/v2/load_balancers/' + load_balancer,
        headers=headers,
    )

    if response1.json()['load_balancer']['status'] == 'overload':
        add_droplet(load_balancer, 'https://github.com/gaurav20303/cldc-project.git')

"""
def scale_down():
    load_balancer = '83ef52cc-7328-4d01-81c7-9b5b82a63cc5'

    remove_droplet(load_balancer, 'https://github.com/gaurav20303/cldc-project.git')
"""

def failover():
    # get all droplets in the load balancer
    # check if all are active
    # add new droplets to the load balancer if there are inactive droplets

    load_balancer = '83ef52cc-7328-4d01-81c7-9b5b82a63cc5'

    response1 = requests.get(
        'https://api.digitalocean.com/v2/load_balancers/' + load_balancer,
        headers=headers,
    )

    droplet_ids = response1.json()['load_balancer']['droplet_ids']

    droplets_to_add = 0
    for droplet in droplet_ids:
        response2 = requests.get('https://api.digitalocean.com/v2/droplets/'+droplet, headers=headers)
        if response2.json()['droplet']['status'] != 'active':
            droplets_to_add += 1

    while droplets_to_add != 0:
        add_droplet(load_balancer, 'https://github.com/gaurav20303/cldc-project.git')
        droplets_to_add -= 1


def add_droplet(load_balancer, code):
    # create new droplet
    json_data = {
        'names': 'extra',
        'region': 'nyc3',
        'size': 's-1vcpu-1gb',
        'image': 'ubuntu-20-04-x64',
        'ssh_keys': [
            37035844,
            '03:fb:11:dc:dd:05:da:89:09:0e:93:56:4f:85:dd:99',
        ],
        'backups': True,
        'ipv6': True,
        'monitoring': True,
        'tags': [
            'env:prod',
            'web',
        ],
        'user_data': '#!/bin/bash\n'
                     'cd ~\n'
                     'sudo apt-get update\n'
                     'sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3 -y\n'
                     'sudo pip3 install virtualenv\n'
                     'mkdir django\n'
                     'cd django\n'
                     'virtualenv myprojectenv\n'
                     'git clone ' + code + '\n'
                     'source myprojectenv/bin/activate\n'
                     'cd cldc-project\n'
                     'echo "STATIC_ROOT = os.path.join(BASE_DIR, \'static/\')" >> cloudProject/settings.py\n'
                     'echo "DIGITALOCEAN_TOKEN=\'dop_v1_1e4fa9c34915414581b26d6fd3749fca938aea7f94e28aca7b3d63d39ee47d0\'" >> cloudProject/settings.py\n'
                     'pip install -r requirements.txt\n'
                     'python3 manage.py collectstatic\n'
                     'python3 manage.py runserver 0.0.0.0:8000\n',

        # 'wget https://cloud-sample-2.s3.ap-south-1.amazonaws.com/deploy.sh\n'
        # 'chmod u+x deploy.sh\n'
        # 'source deploy.sh\n',

        'vpc_uuid': '20cbdb95-0536-48ed-93d6-6de4ee1da7ed',
    }

    response1 = requests.post('https://api.digitalocean.com/v2/droplets', headers=headers, json=json_data)

    time.sleep(60)

    # add newly created droplet to the load balancer
    json_data = {
        'droplet_ids': [response1.json()['droplet']['id']]
    }

    response2 = requests.post(
        'https://api.digitalocean.com/v2/load_balancers/' + load_balancer + '/droplets',
        headers=headers,
        json=json_data,
    )

    if response2.status_code == 200:
        print("Ok")
    else:
        print("Error")


def remove_droplet(load_balancer):

    # get all droplets in the load balancer

    response1 = requests.get(
        'https://api.digitalocean.com/v2/load_balancers/' + load_balancer,
        headers=headers,
    )

    droplet_ids = response1.json()['load_balancer']['droplet_ids']

    # delete a droplet from the load balancer

    json_data = {
        'droplet_ids': [
            droplet_ids[-1]
        ],
    }

    response2 = requests.delete(
        'https://api.digitalocean.com/v2/load_balancers/' + load_balancer + '/droplets',
        headers=headers,
        json=json_data,
    )
