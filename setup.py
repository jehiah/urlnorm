from distutils.core import setup

setup(name='urlnorm',
        version='1.0',
        long_description=open("./README.txt", "r").read(),
        description="Normalize a URL to a standard unicode encoding",
        py_modules=['urlnorm'],
        license='MIT License',
        author='Jehiah Czebotar',
        author_email='"Jehiah Czebotar" <jehiah@gmail.com>',
        url='http://github.com/jehiah/urlnorm',
        )
