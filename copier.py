import os
from secret import remotepath, remotehost
from data import replace

filename = 'index.html'
remotefile = os.path.join(remotepath, filename)


def copy_to_remote():
    os.system(f'scp "{filename}" "{remotehost}:{remotefile}"')


def copy_from_remote():
    os.system(f'scp "{remotehost}:{remotefile}" "{filename}"')


if __name__ == "__main__":
    copy_from_remote()
    replace(filename)
    copy_to_remote()
