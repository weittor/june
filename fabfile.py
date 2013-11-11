# coding: utf-8

import os
from fabric.api import env, local, cd, run, sudo
from fabric.operations import put

env.user = 'www'
env.hosts = ['python-china.org']
# env.password


def prepare():
    """Prepare server for installation."""
    run('mkdir -p ~/venv')
    run('virtualenv ~/venv/june')
    run('mkdir -p ~/apps/june/public/static')
    run('mkdir -p ~/apps/june/public/data')


def tarball():
    """Create tarball for june."""
    local('make static')
    local('python setup.py sdist --formats=gztar', capture=False)
    local('rm -fr etc')
    local('mv etc-bak etc')


def upload():
    """Upload tarball to the server."""
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/%s.tar.gz' % dist, '~/tmp/june.tar.gz')

    run('mkdir -p ~/tmp/june')
    with cd('~/tmp/june'):
        run('tar xzf ~/tmp/june.tar.gz')


def install():
    """Install june package."""
    dist = local('python setup.py --fullname', capture=True).strip()
    with cd('~/tmp/june/%s' % dist):
        run('~/venv/june/bin/python setup.py install')


def clean():
    """Clean packages on server."""
    run('rm -fr ~/tmp/june')
    run('rm -f ~/tmp/june.tar.gz')



def configure():
    """Prepare configuration files."""
    dist = local('python setup.py --fullname', capture=True).strip()
    tmpdir = '~/tmp/june/%s' % dist

    run('cp %s/wsgi.py ~/apps/june/' % tmpdir)
    run('cp %s/manager.py ~/apps/june/' % tmpdir)
    run('cp %s/alembic.ini ~/apps/june/' % tmpdir)
    run('cp -r %s/alembic ~/apps/june/' % tmpdir)


def upgrade():
    """Upgrade database"""
    dist = local('python setup.py --fullname', capture=True).strip()
    tmpdir = '~/tmp/june/%s' % dist
    run('cp %s/alembic.ini ~/apps/yuehu/' % tmpdir)
    run('rm -fr ~/apps/yuehu/alembic')
    run('cp -r %s/alembic ~/apps/yuehu/' % tmpdir)
    with cd('~/apps/june'):
        run('~/venv/june/bin/alembic upgrade head')
