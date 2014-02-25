from fabric.api import task, local, shell_env, env
from pipes import quote


def runcmd(*args):
    args += (
        '--pythonpath=.',
        '--settings=frinat.settings',
        '--configuration=Config',
    )
    args = [quote(a) for a in args]

    database = 'postgres://{}:{}@localhost/{}'.format(env.db_user, env.db_pwd,
                                                      env.db_name)

    with shell_env(DATABASE_URL=database, DJANGO_DEBUG='yes'):
        local('./manage.py {}'.format(' '.join(args)))


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
