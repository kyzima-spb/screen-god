# -*- coding: utf-8 -*-

import platform
import warnings
import subprocess
import time

import psutil

try:
    import win32gui
    import win32process
except ImportError:
    pass

from .messages import _ as t


def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    status = p.wait()
    return output.strip().decode('utf-8'), err, status


class WindowManager(object):
    def find_by_pid(self, pid):
        raise NotImplementedError('WindowManager.find_by_pid() is abstract and must be overridden')

    def find_by_title(self, title):
        raise NotImplementedError('WindowManager.find_by_title() is abstract and must be overridden')

    def geometry(self, hwnd):
        raise NotImplementedError('WindowManager.geometry() is abstract and must be overridden')

    def is_exists(self, hwnd):
        raise NotImplementedError('WindowManager.is_exists() is abstract and must be overridden')

    def move(self, hwnd, x, y, width, height):
        raise NotImplementedError('WindowManager.move() is abstract and must be overridden')

    def Popen(self, *args, attempts=10, **kwargs):
        proc = psutil.Popen(*args, **kwargs)

        while attempts:
            time.sleep(0.5)

            if not psutil.pid_exists(proc.pid):
                raise psutil.NoSuchProcess(proc.pid)

            hwnd = self.find_by_pid(proc.pid)

            if hwnd:
                return hwnd, proc

            attempts -= 1

        raise RuntimeError(t('started_process_without_gui'))


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

    def find_by_mouse_click(self):
        print('Please select window...')

        hwnd, err, code = run_command('xdotool selectwindow')

        if code == 0:
            return hwnd

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

        cmd = 'xdotool getwindowgeometry --shell {}'.format(self.__hwnd2int(hwnd))
        result = run_command(cmd)
        result = result[0].split()

        geometry = {}
        props = {
            'window': 'hwnd',
            'x': 'left',
            'y': 'top',
            'width': 'width',
            'height': 'height',
            'screen': 'screen',
        }

        for p in result:
            prop, value = p.split('=')
            prop = props.get(prop.lower())
            if prop:
                geometry[prop] = int(value)

        return geometry

    def is_exists(self, hwnd):
        _, _, code = run_command('wmctrl -l | grep {}'.format(self.__hwnd2hex(hwnd)))
        return code == 0

    def move(self, hwnd, x, y, width, height):
        run_command('xdotool windowmove {id} {x} {y} windowsize {id} {width} {height} windowraise {id}'.format(
            id=self.__hwnd2int(hwnd),
            x=x,
            y=y,
            width=width,
            height=height
        ))


class WinWindowManager(WindowManager):
    # def borders(self, hwnd):
    #     print(win32gui.GetClientRect(hwnd))
    #     print(win32gui.GetWindowRect(hwnd))

    # def find_by_mouse_click(self):
        # WindowFromPoint

    def find_by_pid(self, pid):
        if not psutil.pid_exists(pid):
            return None

        hwnd_found = None

        def cb(hwnd, pid_needed):
            nonlocal hwnd_found

            if not win32gui.IsWindowVisible(hwnd):
                return

            tid, pid = win32process.GetWindowThreadProcessId(hwnd)

            if pid == pid_needed:
                hwnd_found = hwnd

        win32gui.EnumWindows(cb, pid)

        return hwnd_found

    def find_by_title(self, title):
        return win32gui.FindWindow(None, title)

    def geometry(self, hwnd):
        if self.is_exists(hwnd):
            rect = win32gui.GetWindowRect(hwnd)

            return {
                'hwnd': hwnd,
                'left': rect[0],
                'top': rect[1],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1],
                'screen': None,
            }

    def get_all_opened(self):
        """Get all the open windows, that have WS_VISIBLE style."""

        opened = []

        def create_opened_callback(hwnd, opened):
            if win32gui.IsWindowVisible(hwnd):
                opened.append(hwnd)

        win32gui.EnumWindows(create_opened_callback, opened)

        return opened

    def is_exists(self, hwnd):
        return bool(win32gui.IsWindow(hwnd))

    def move(self, hwnd, x, y, width, height):
        if self.is_exists(hwnd):
            win32gui.MoveWindow(hwnd, x, y, width, height, True)

    def Popen(self, *args, attempts=10, **kwargs):
        """
        Обработчик исключения psutil.NoSuchProcess необходим по причине:

        В Windows некоторые приложения при повторном запуске не создают нового процесса, а порождают новый поток.

        Поэтому, возвращаемый методом Popen, объект Process становится бесполезным
        и порожденный им процесс через некоторое время будет убит.
        """

        opened = self.get_all_opened()

        try:
            return super().Popen(*args, attempts=attempts, **kwargs)
        except psutil.NoSuchProcess:
            while attempts:
                last_opened = set(self.get_all_opened()) - set(opened)

                if len(last_opened):
                    return opened.pop(), None

                attempts -= 1
                time.sleep(0.5)

            raise RuntimeError(t('started_process_without_gui'))


osname = platform.system()

if osname == 'Windows':
    WindowManager = WinWindowManager()
elif osname == 'Linux':
    def check_installed(package_name):
        _, _, code = run_command('which {}'.format(package_name))

        if code:
            warnings.warn('''I require "{}" but it's not installed.'''.format(package_name),
                          stacklevel=2)

    check_installed('xdotool')
    check_installed('wmctrl')

    WindowManager = LinuxWindowManager()
elif osname == 'Darwin':
    raise ImportError('MacOS is not yet supported')
else:
    raise ImportError('Your platform is not supported')
