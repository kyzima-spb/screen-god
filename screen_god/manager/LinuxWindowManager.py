# -*- coding: utf-8 -*-

import psutil

from screen_god.common import run_command
from screen_god.manager.WindowManager import WindowManager


class LinuxWindowManager(WindowManager):
    def __hwnd2int(self, hwnd):
        hwnd = str(hwnd)
        return int(hwnd) if hwnd.isdigit() else int(hwnd, 16)

    def __hwnd2hex(self, hwnd):
        return format(hwnd, '#010x')

    def borders(cls, hwnd):
        # свернуть, если окно развернуто на весь экран
        cmd = 'wmctrl -i -r {} -b remove,maximized_vert,maximized_horz'.format(hwnd)
        run_command(cmd)

        cmd = 'xprop _NET_FRAME_EXTENTS -id {} | egrep -o [0-9]+'.format(hwnd)
        result = run_command(cmd)

        props = ['left', 'right', 'top', 'bottom']
        borders = {}

        for prop, value in zip(props, result[0].split()):
            borders[prop] = int(value)

        return borders

    def close(self, hwnd):
        res, err, code = run_command('xkill -id {}'.format(hwnd))

    def find_by_mouse_click(self):
        print('Please select window...')

        hwnd, err, code = run_command('xwininfo | grep "Window id:" | cut -f 4 -d \ ')

        if code == 0:
            return self.__hwnd2int(hwnd)

    def find_by_pid(self, pid):
        if not psutil.pid_exists(pid):
            return None

        result = run_command('wmctrl -l -p | grep {} | cut -f1 -d\ '.format(pid))

        return self.__hwnd2int(result[0]) if result[0] else None

    def find_by_title(self, title):
        result = run_command('wmctrl -l | grep "{}" | cut -f1 -d\ '.format(title))
        return self.__hwnd2int(result[0]) if result[0] else None

    def geometry(self, hwnd):
        """Returns without borders"""

        cmd = 'xwininfo -id {} | egrep "(Absolute|Width|Height)" | egrep -o "[a-zA-Z]+:.*[0-9]+"'.format(
            self.__hwnd2int(hwnd)
        )

        result, err, code = run_command(cmd)
        result = [i.split(':') for i in result.split('\n')]
        result = dict([p.strip().lower(), int(v.strip())] for p, v in result)

        borders = self.borders(hwnd)

        geometry = {
            'hwnd': hwnd,
            'left': result['x'] - borders['left'],
            'top': result['y'] - borders['top'],
            'width': result['width'] + borders['left'] + borders['right'],
            'height': result['height'] + borders['top'] + borders['bottom'],
        }

        return geometry

    def get_opened(self):
        """Get all the open windows."""
        opened, _, _ = run_command('wmctrl -l | cut -f 1 -d \ ')
        return opened.split()


    def is_exists(self, hwnd):
        _, _, code = run_command('wmctrl -l | grep {}'.format(self.__hwnd2hex(hwnd)))
        return code == 0

    def move(self, hwnd, x, y, width, height):
        borders = self.borders(hwnd)

        run_command('wmctrl -i -r {id} -b remove,maximized_vert,maximized_horz -e 0,{x},{y},{width},{height}'.format(
            id=hwnd,
            x=x,
            y=y,
            width=width - borders['left'] - borders['right'],
            height=height - borders['top'] - borders['bottom']
        ))
