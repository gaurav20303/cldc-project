from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
import os
import requests


def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'beanstalk/index.html')

def create_app(request):
    name = request.POST.get('name', None)
    platform = request.POST.get('platform', None)
    platform_branch = request.POST.get('platform_branch', None)
    platform_version = request.POST.get('platform_version', None)
    code = request.POST.get('code', None)

    #DIGITALOCEAN_TOKEN = os.getenv('DIGITALOCEAN_TOKEN')
    DIGITALOCEAN_TOKEN = 'dop_v1_d9d78fb794940a48b79229e66c2b457abd65dcccfb04bebdc0234827a51eaed7'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
    }

    json_data = {
        'name': name,
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
        'user_data': '#cloud-config\nruncmd:\n  - touch /test.txt\n',
        'vpc_uuid': '20cbdb95-0536-48ed-93d6-6de4ee1da7ed',
    }

    response = requests.post('https://api.digitalocean.com/v2/droplets', headers=headers, json=json_data)
    #return HttpResponse(str(response.text))

    if 'droplet' in response.json():
        return JsonResponse({'success': True, 'data': response.json()})
    else:
        return JsonResponse({'success': False})
