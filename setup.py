from distutils.core import setup
setup(
  name = 'serverutils',
  packages = ['serverutils'],
  version = '1.5',
  description = 'A python library for webserver development with a simple API',
  author = 'Noman',                   # Type in your name
  author_email = 'plupy44@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/LinuxRocks2000/netutils',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/LinuxRocks2000/netutils/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['socket', 'websockets', 'tcp', 'web', 'server'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'websockets',
  ],
)
