from fabric.api import task, local, shell_env, env
from fabric.state import output

from pipes import quote


def runcmd(*args):
    args += (
        '--pythonpath=.',
        '--settings=frinat.settings',
        '--configuration=Config',
    )
    args = [quote(a) for a in args]

    with shell_env(**env.django_env):
        local('./manage.py {}'.format(' '.join(args)))


@task(name='env')
def getenv():
    """
    Call in this way: fab -H running env | source /dev/stdin
    """
    output['status'] = False
    for k, v in sorted(env.django_env.items()):
        print 'export {}={}'.format(k, quote(v))


@task
def fixdb():
    #local('workon frinat-db-fixer && ./manage.py syncdb')
    #local('workon frinat-db-fixer && ./manage.py migrate')
    runcmd('syncdb')
    runcmd('migrate')
    runcmd('cms', 'delete_orphaned_plugins')
    runcmd('cms', 'moderator', 'on')
    runcmd('cms', 'uninstall', 'apphooks', 'zinnia')
    runcmd('cms', 'check')


@task
def serve():
    runcmd('runserver', '0.0.0.0:8000')
