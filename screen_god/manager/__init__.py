# -*- coding: utf-8 -*-

import platform
import warnings

from screen_god.common import run_command


osname = platform.system()

if osname == 'Windows':
    from screen_god.manager.WinWindowManager import WinWindowManager

    WindowManager = WinWindowManager()
elif osname == 'Linux':
    from screen_god.manager.LinuxWindowManager import LinuxWindowManager

    def check_installed(package_name):
        _, _, code = run_command('which {}'.format(package_name))

        if code:
            warnings.warn('''I require "{}" but it's not installed.'''.format(package_name),
                          stacklevel=2)

    check_installed('wmctrl')

    WindowManager = LinuxWindowManager()
elif osname == 'Darwin':
    raise ImportError('MacOS is not yet supported')
else:
    raise ImportError('Your platform is not supported')
