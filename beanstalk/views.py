from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
import os
import requests
import select
import paramiko
import time

from cloudProject import settings


def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'beanstalk/index.html')

def create_app(request):
    name = request.POST.get('name', None)
    platform = request.POST.get('platform', None)
    platform_branch = request.POST.get('platform_branch', None)
    platform_version = request.POST.get('platform_version', None)
    code = request.POST.get('code', None)

    DIGITALOCEAN_TOKEN = settings.DIGITALOCEAN_TOKEN

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
    }

    json_data = {
        'names': [name+'-01',
                  name+'-02',
                  name+'-03'],
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
                     'wget https://cloud-sample-2.s3.ap-south-1.amazonaws.com/deploy.sh\n'
                     'chmod u+x deploy.sh\n'
                     'source deploy.sh\n',

        'vpc_uuid': '20cbdb95-0536-48ed-93d6-6de4ee1da7ed',
    }

    response = requests.post('https://api.digitalocean.com/v2/droplets', headers=headers, json=json_data)
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

    if 'droplets' in response.json():
        return JsonResponse({'success': True, 'data': response.json()})
    else:
        return JsonResponse({'success': False})


