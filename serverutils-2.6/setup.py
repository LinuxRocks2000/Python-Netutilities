from distutils.core import setup
setup(
  name = 'serverutils',
  packages = ['serverutils',"clientutils"],
  version = '2.6',
  description = 'A python library for webserver development with a simple API',
  author = 'Noman',
  author_email = 'plupy44@gmail.com',
  url = 'https://github.com/LinuxRocks2000/netutils',
  download_url = 'https://github.com/LinuxRocks2000/netutils/archive/v_01.tar.gz',
  keywords = ['socket', 'websockets', 'tcp', 'web', 'server'],
  install_requires=[
          'htmlib', ## A library I made myself.
  ],
)
