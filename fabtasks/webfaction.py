import os
from fabric.api import env, task, local, hide, put, run, get
from fabric.contrib.project import rsync_project
import pipes
import xmlrpclib
import functools


APACHE_START_SCRIPT = r"""
#!/bin/bash

/home/frinat/bin/envdir /home/frinat/webapps/{appname}/conf \\
        /home/frinat/webapps/{appname}/apache2/bin/httpd.worker \\
        -f /home/frinat/webapps/{appname}/apache2/conf/httpd.conf \\
        -k start
"""

APACHE_CONF = r"""
ServerRoot "/home/frinat/webapps/{appname}/apache2"

LoadModule dir_module        modules/mod_dir.so
LoadModule env_module        modules/mod_env.so
LoadModule log_config_module modules/mod_log_config.so
LoadModule mime_module       modules/mod_mime.so
LoadModule rewrite_module    modules/mod_rewrite.so
LoadModule setenvif_module   modules/mod_setenvif.so
LoadModule wsgi_module       modules/mod_wsgi.so

LogFormat "%{{X-Forwarded-For}}i %l %u %t \\"%r\\" %>s %b \\"%{{Referer}}i\\" \\"%{{User-Agent}}i\\"" combined
CustomLog /home/frinat/logs/user/access_{appname}.log combined
ErrorLog /home/frinat/logs/user/error_{appname}.log

KeepAlive Off
Listen {port}
MaxSpareThreads 3
MinSpareThreads 1
ServerLimit 1
SetEnvIf X-Forwarded-SSL on HTTPS=1
ThreadsPerChild 5

WSGIPythonHome /home/frinat/webapps/{appname}
WSGIScriptAlias / /home/frinat/webapps/{appname}/lib/python2.7/site-packages/frinat/wsgi.py
WSGIDaemonProcess {appname} processes=2 python-path=/home/frinat/webapps/{appname}/lib/python2.7 threads=12
WSGIProcessGroup {appname}
WSGIRestrictEmbedded On
WSGILazyInitialization On
"""


def runl(*args, **kwargs):
    args = [pipes.quote(a) for a in args]
    return run(' '.join(args), **kwargs)


@task
def backupdb():
    dumpfile = '/home/frinat/db.dump.tmp'

    runl(
        'pg_dump',
        '--clean',
        '--blobs',
        '--format', 'custom',
        '--no-owner',
        '--no-password',
        '--oids',
        '--no-privileges',
        '--host', 'localhost',
        '--port', '5432',
        '--compress', '9',
        '--username', env.webfaction_db_user,
        '--file', dumpfile,
        env.webfaction_db_name,
    )
    get(dumpfile, 'db.dump')
    runl('rm', '-f', dumpfile)


@task
def syncoldmedia():
    rsync_project(
        remote_dir='/home/frinat/webapps/staging/stages/test03/static/assets',
        local_dir='_dev/media',
        upload=False,
        delete=True,
    )


def dnsping(domain, server):
    pass


def get_main_ip(api):
    ips = api.list_ips()
    for info in ips:
        if info['is_main']:
            return info['ip']
    else:
        raise RuntimeError('Main server not found.')


def get_current_revision():
    with hide('everything'):
        return str(local('git log -n 1 --format=\'%h\'', capture=True))


class AuthenticationError(Exception):
    pass


class WebfactionAPI(object):
    endpoint = 'https://api.webfaction.com/'

    def __init__(self, username, password):
        self.server = xmlrpclib.ServerProxy(self.endpoint)

        try:
            self.session_id, _ = self.server.login(username, password)
        except xmlrpclib.Fault as e:
            raise AuthenticationError(e.faultCode, e.faultString)

    def __getattr__(self, name):
        assert self.session_id, 'Login before executing any action'
        return functools.partial(getattr(self.server, name), self.session_id)


class RevisionApp(object):
    prefix = 'frinat_'
    domain = 'fribourg-natation.ch'
    app_type = 'mod_wsgi33-python27'

    def __init__(self, api, revision, is_active=False):
        self.revision = revision
        self.is_active = is_active
        self.api = api

    def __str__(self):
        return 'RevisionApp({!r}, {!r})'.format(self.domain, self.revision)

    @property
    def subdomain(self):
        return str(self.revision)

    @property
    def fqdn(self):
        return '{}.{}'.format(self.subdomain, self.domain)

    @property
    def appname(self):
        return '{}{}'.format(self.prefix, self.revision)

    @classmethod
    def active_revision(cls, api):
        active = '{}active'.format(cls.prefix)
        for website in api.list_websites():
            if website['name'] == active:
                for app, _ in website['website_apps']:
                    if app.startswith(cls.prefix):
                        rev = app[len(cls.prefix):]
                        if rev not in ['static', 'media']:
                            return rev

    @classmethod
    def iterall(cls, api):
        active = cls.active_revision(api)
        for app in api.list_apps():
            if app['name'].startswith(cls.prefix):
                revision = app['name'][len(cls.prefix):]
                if revision not in ['static', 'media']:
                    yield cls(api, revision, revision == active)

    def _log(self, msg, *args, **kwargs):
        print msg.format(*args, **kwargs)

    def deploy(self):
        ip = get_main_ip(self.api)
        appname = self.appname

        self._log('Creating app...')
        self.api.create_app(appname, self.app_type, True, '', False)

        self._log('Creating domain...')
        self.api.create_domain(self.domain, self.subdomain)

        self._log('Creating website...')
        self.api.create_website(appname, ip, False, [self.fqdn],
                                [appname, '/'],
                                ['frinat_static', '/static'],
                                ['frinat_media', '/media'])

        self._install()
        self._restart()

    def _install(self):
        appname = self.appname
        build_name = 'frinat_www-0.1.0-py27-none-any.whl'
        port = self.api.system(
            'grep Listen /home/frinat/webapps/{}/apache2/conf/httpd.conf'
            .format(self.appname)
        ).strip().split(' ', 1)[1]

        # Build distribution
        self._log('Building distribution (locally)...')
        local('python setup.py bdist_wheel')

        # Upload distribution
        self._log('Uploading package...')
        put(os.path.join('dist', build_name),
            '/home/frinat/webapps/{}/{}'.format(appname, build_name))

        # Create and setup virtualenv
        self._log('Creating virtualenv...')
        run('/home/frinat/bin/virtualenv-2.7 --python=/usr/local/bin/python2.7'
            ' /home/frinat/webapps/{}'.format(appname))
        run('/home/frinat/webapps/{}/bin/pip install wheel'.format(appname))

        # Install package and dependencies
        self._log('Installing dependencies...')
        run('/home/frinat/webapps/{}/bin/pip install --no-index -I -f '
            '/home/frinat/wheelhouse /home/frinat/webapps/{}/{}'
            .format(appname, appname, build_name))
        put('manage.py', '/home/frinat/webapps/{}/bin/manage.py'
            .format(appname))

        # Configure webserver
        self._log('Configuring webserver...')

        run('rm -rf /home/frinat/webapps/{}/htdocs'.format(appname))
        run('mkdir /home/frinat/webapps/{}/conf'.format(appname))

        self._setopt('DATABASE_URL', 'postgres://{}:{}@localhost/{}'.format(
            env.webfaction_db_user,
            env.webfaction_db_pwd,
            env.webfaction_db_name,
        ))
        self._setopt('DJANGO_MEDIA_ROOT', '/home/frinat/webapps/frinat_media')
        self._setopt('DJANGO_STATIC_ROOT',
                     '/home/frinat/webapps/frinat_static')
        self._setopt('LD_LIBRARY_PATH',
                     '/home/frinat/webapps/{}/apache2/lib'.format(appname))

        self.api.write_file(
            '/home/frinat/webapps/{}/apache2/conf/httpd.conf'.format(appname),
            APACHE_CONF.format(appname=appname, port=port).strip(),
        )
        self.api.write_file(
            '/home/frinat/webapps/{}/apache2/bin/start'.format(appname),
            APACHE_START_SCRIPT.format(appname=appname).strip(),
        )

    def _setopt(self, name, value):
        self.api.write_file(
            '/home/frinat/webapps/{}/conf/{}'.format(self.appname, name),
            value,
        )

    def _restart(self):
        self._log('Restarting webserver...')
        self._log(run('/home/frinat/webapps/{}/apache2/bin/restart'
                      .format(self.appname)))

    def _run_django(self, *cmd):
        envdir = '/home/frinat/bin/envdir'
        confdir = '/home/frinat/webapps/{}/conf'.format(self.appname)
        executable = (
            '/home/frinat/webapps/{0}/bin/python '
            '/home/frinat/webapps/{0}/bin/manage.py'.format(self.appname)
        )
        args = [pipes.quote(c) for c in cmd] + [
            '--settings=frinat.settings',
            '--configuration=Config',
        ]
        run('{} {} {} {}'.format(envdir, confdir, executable, ' '.join(args)))

    def collectstatic(self):
        self._run_django('collectstatic')

    def promote(self):
        ip = get_main_ip(self.api)
        self.api.update_website('{}active'.format(self.prefix), ip, False,
                                [self.domain, 'www.{}'.format(self.domain)])
        self.api.update_website('{}active'.format(self.prefix), ip, False,
                                [self.domain, 'www.{}'.format(self.domain)],
                                [self.appname, '/'],
                                ['frinat_static', '/static'],
                                ['frinat_media', '/media'])

    def destroy(self):
        ip = get_main_ip(self.api)
        appname = self.appname

        self._log('Stopping webserver')
        run('/home/frinat/webapps/{}/apache2/bin/stop'.format(appname))

        self._log('Destroying website...')
        self.api.delete_website(appname, ip, False)

        self._log('Destroying domain...')
        self.api.delete_domain(self.domain, self.subdomain)

        self._log('Destroying app...')
        self.api.delete_app(appname)


@task
def reqs():
    api = WebfactionAPI(env.webfaction_username, env.webfaction_password)

    try:
        with open('requirements.txt') as fh:
            api.write_file('requirements.txt.tmp', fh.read())
        run('~/wheels-builder/bin/pip wheel -r requirements.txt.tmp')
    finally:
        run('rm -f requirements.txt.tmp')


@task
def list_instances():
    api = WebfactionAPI(env.webfaction_username, env.webfaction_password)
    apps = list(RevisionApp.iterall(api))

    if apps:
        for i, app in enumerate(apps):
            print ' {}. {} {}'.format(i + 1, app.revision,
                                      '*' if app.is_active else '')
    else:
        print 'No instances found.'


class RevisionMethodCaller(object):
    def __init__(self, method):
        self.method = method

    @classmethod
    def build(cls, method):
        return task(cls(method))

    def __call__(self, rev=None, *args, **kwargs):
        if rev is None:
            rev = get_current_revision()
        api = WebfactionAPI(env.webfaction_username, env.webfaction_password)
        app = RevisionApp(api, rev)
        method = getattr(app, self.method)
        return method(*args, **kwargs)


promote = RevisionMethodCaller.build('promote')
collectstatic = RevisionMethodCaller.build('collectstatic')
fixdb = RevisionMethodCaller.build('fixdb')
deploy = RevisionMethodCaller.build('deploy')
destroy = RevisionMethodCaller.build('destroy')
