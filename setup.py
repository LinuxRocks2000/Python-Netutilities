from distutils.core import setup
setup(
  name = 'serverutils',         # How you named your package folder (MyLib)
  packages = ['serverutils'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Some simple server-making utilities for python3',   # Give a short description about your library
  author = 'Frake Namir',                   # Type in your name
  author_email = 'your.email@domain.com',      # Type in your E-Mail
  url = 'https://github.com/LinuxRocks2000/netutils/',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/LinuxRocks2000/netutils/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['TCP', 'server', 'website'],   # Keywords that define your package best
  install_requires=[
  'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
