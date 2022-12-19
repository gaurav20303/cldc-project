from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
import os
import requests
import select
import paramiko
import time
import datetime

from cloudProject import settings


def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'beanstalk/index.html')


def create_app(request):
    name = request.POST.get('name', None)
    platform = request.POST.get('platform', None)
    platform_branch = request.POST.get('platform_branch', None)
    platform_version = request.POST.get('platform_version', None)
    size = request.POST.get('size', None)
    image = request.POST.get('image', None)
    code = request.POST.get('code', None)

    DIGITALOCEAN_TOKEN = settings.DIGITALOCEAN_TOKEN

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
    }

    json_data = {
        'names': [name + '-01',
                  name + '-02',
                  name + '-03'],
        'region': 'nyc3',
        'size': size,
        'image': image,
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
                     'echo "ALLOWED_HOSTS=[\'*\']" >> cloudProject/settings.py\n'
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
    log(response1.text)

    droplet_ids = []
    for droplet in response1.json()['droplets']:
        # log(str(droplet['id']))
        droplet_ids.append(droplet['id'])

    # return HttpResponse(str(response.text))

    # os.system('ssh root@142.93.66.240')
    # os.system('wget https://cloud-sample-2.s3.ap-south-1.amazonaws.com/deploy.sh')
    # os.system('chmod u+x deploy.sh')

    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    time.sleep(60)
    response = requests.get('https://api.digitalocean.com/v2/droplets/'+str(response.json()['droplet']['id']), headers=headers)

    # '142.93.66.240'
    #return HttpResponse(str(response.json()['droplet']['networks']['v4'][0]['ip_address']))
    ip = str(response.json()['droplet']['networks']['v4'][0]['ip_address'])
    ssh.connect(ip, port=22, username='root', timeout=5)

    cmd_list = ['wget https://cloud-sample-2.s3.ap-south-1.amazonaws.com/deploy.sh',
                'chmod u+x deploy.sh',
                'source deploy.sh'
                ]

    for command in cmd_list:
        # print command
        # print("> " + command)
        # execute commands
        stdin, stdout, stderr = ssh.exec_command(command)
        # TODO() : if an error is thrown, stop further fules
        # Wait for the command to terminate
        while not stdout.channel.exit_status_ready():
            # Only print data if there is data to read in the channel
            if stdout.channel.recv_ready():
                rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                if len(rl) > 0:
                    tmp = stdout.channel.recv(1024)
                    output = tmp.decode()
                    # print(output)

    # Close SSH connection
    ssh.close()
    """

    time.sleep(60)

    # create a load balancer
    json_data = {
        'name': name + '-lb',
        'size_unit': 1,
        'region': 'nyc3',
        'forwarding_rules': [
            {
                'entry_protocol': 'http',
                'entry_port': 80,
                'target_protocol': 'http',
                'target_port': 8000,
                'certificate_id': '',
                'tls_passthrough': False,
            },
            {
                'entry_protocol': 'https',
                'entry_port': 444,
                'target_protocol': 'https',
                'target_port': 443,
                'tls_passthrough': True,
            },
        ],
        'health_check': {
            'protocol': 'http',
            'port': 80,
            'path': '/',
            'check_interval_seconds': 10,
            'response_timeout_seconds': 5,
            'healthy_threshold': 5,
            'unhealthy_threshold': 3,
        },
        'sticky_sessions': {
            'type': 'none',
        },
        'droplet_ids': droplet_ids,
        'vpc_uuid': '20cbdb95-0536-48ed-93d6-6de4ee1da7ed'
    }

    response2 = requests.post('https://api.digitalocean.com/v2/load_balancers', headers=headers, json=json_data)
    log(response2.text)

    time.sleep(120)

    response3 = requests.get(
        'https://api.digitalocean.com/v2/load_balancers/' + response2.json()['load_balancer']['id'],
        headers=headers,
    )
    log(response3.text)

    if response3.status_code == 200:
        return JsonResponse({'success': True, 'data': response3.json()['load_balancer']['ip']})
    else:
        return JsonResponse({'success': False})


def log(text):
    f = open("log.txt", "a")
    f.write('\n'+str(datetime.datetime.now()) + ' ' + text)
    f.close()
