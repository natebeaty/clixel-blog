from fabric import task, Connection
from invoke import run as local
from patchwork.transfers import rsync

remote_path = "/home/natebeaty/apps/clixel-blog/"
remote_hosts = ["natebeaty@natebeaty.com"]
php_command = "php74"

# deploy
@task(hosts=remote_hosts)
def deploy(c):
    build(c)
    upload(c)

def upload(c):
    rsync(c, "public/", remote_path)

# local commands
@task
def build(c):
    local("hugo -D")
