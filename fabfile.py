from os.path import join, dirname, exists
from glob import glob
from fabric.api import env


def sibling(*args):
    return join(dirname(__file__), *args)


def loadenv(path):
    if not exists(path):
        return
    gl = {}
    execfile(path, gl)
    for k, v in gl.iteritems():
        if not k.startswith('_'):
            setattr(env, k, v)


loadenv(sibling('fabenv.py'))

for f in glob(sibling('fabtasks', '*.py')):
    execfile(f)
