---
title: "Moving from Fabric 1.x to Fabric 2.x"
date: 2021-01-07T17:48:39-05:00
slug: "moving-from-fabric-1-to-fabric-2"
---

I've long used Fabric for simple deploy scripts to essentially ssh in, `git pull`, `composer install` or `bundle`, restart apps, clear caches, etc. It's also handy for local dev shortcuts like `fab assets` as a stand-in for the more wordy `npx gulp --production` or `fab dev` to simultaneously fire up sphinx, a tornado websocket app, gulp, etc.

With a new M1 MacBook Air, I ran into issues getting `fabric@1.4` to play nicely with homebrew, and decided to once again try my hand at converting my super simple deploy scripts to the new v2 syntax. Information is scarce on sample Fabric 2 scripts, but I did find an aptly titled post "[Why Is Fabric 2 so Hard?](https://vsupalov.com/fabric-2-example-fabfile/)" which helped me get started.

There's an [upgrade guide](http://www.fabfile.org/upgrading.html), but my god it's complicated, until it's not complicated enough with the sample v1->v2 migration at the end of the page.

Here's my simple v1 fabfile.py:

    from fabric.api import *

    env.hosts = ['natebeaty.opalstacked.com']
    env.user = 'deploy'
    env.remotepath = '/home/natebeaty/apps/nb-craft-staging'
    env.git_branch = 'master'
    env.forward_agent = True
    env.php_binary = 'php74'

    def production():
      env.remotepath = '/home/natebeaty/apps/nb-craft-staging'
      env.hosts = ['natebeaty.com']

    def assets():
      local('npx gulp --production')

    def deploy(composer='y'):
      update()
      if composer == 'y':
        composer_install()
      clear_cache()

    def update():
      with cd(env.remotepath):
        run('git pull origin {0}'.format(env.git_branch))

    def composer_install():
      with cd(env.remotepath):
        run('%s ~/bin/composer.phar install' % env.php_binary)

    def clear_cache():
      with cd(env.remotepath):
        run('./craft clear-caches/compiled-templates')
        run('./craft clear-caches/data')

And this is where I'm at so far with a functional v2 version:

    from fabric import task
    from invoke import run as local

    remote_path = "/home/natebeaty/apps/nb-craft-staging"
    remote_hosts = ["deploy@natebeaty.opalstacked.com"]
    php_command = "php74"

    # set to production
    @task
    def production(c):
        global remote_hosts, remote_path
        remote_hosts = ["deploy@natebeaty.com"]
        remote_path = "/home/natebeaty/apps/nb-craft-production"

    # deploy
    @task(hosts=remote_hosts)
    def deploy(c):
        update(c)
        composer_update(c)
        clear_cache(c)

    def update(c):
        c.run("cd {} && git pull".format(remote_path))

    def composer_update(c):
        c.run("cd {} && {} ~/bin/composer.phar install".format(remote_path, php_command))

    def clear_cache(c):
        c.run("cd {} && ./craft clear-caches/compiled-templates".format(remote_path))
        c.run("cd {} && ./craft clear-caches/data".format(remote_path))

    # local commands
    @task
    def assets(c):
        local("npx gulp --production")

Still a few things to port over, but it's working well enough. The part that feels ugly is the use of `global` in `production()`, but I couldn't find any examples of how folks are overriding connection configs in a Fabric v2 file.

Using `c.local()` I was getting errors finding `npx` because my $PATH was different, missing the M1 homebrew `/opt/homebrew/bin`. This [StackOverflow comment](https://stackoverflow.com/questions/51793744/how-do-i-run-a-local-command-with-fabric-2#comment109146032_55704170) pointed me to using `from invoke import run as local` then `local()` instead of `c.local()`. This fixed my $PATH issues and `npx gulp` worked fine.
