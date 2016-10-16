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

from .messages import t


def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    status = p.wait()
    return output.strip().decode('utf-8'), err, status


class WindowManager(object):
    def find_by_pid(self, pid):
        """Найти окно по идентификатору процесса."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.find_by_pid()'))

    def find_by_title(self, title):
        """Найти окно по заголовку, используется точное совпадение."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.find_by_title()'))

    def geometry(self, hwnd):
        """Возвращает позицию и размеры окна относительно экрана."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.geometry()'))

    def is_exists(self, hwnd):
        """Возвращает True, если окно с указанным идентификатором существует."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.is_exists()'))

    def move(self, hwnd, x, y, width, height):
        """Изменяет размеры окна и перемещает его в указанную позицию."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.move()'))

    def Popen(self, args, attempts=10, shell=False, **kwargs):
        """
        Порождает новый процесс и пытается найти открывшееся окно.
        В случаи успеха будет возвращен идентификатор окна и процесс.
        В случаи неудачи, будет возбуждено исключение.
        """
        def get_children(proc, attempts):
            children = []

            while attempts and len(children) == 0:
                time.sleep(0.5)

                if not psutil.pid_exists(proc.pid):
                    raise psutil.NoSuchProcess(proc.pid)

                children = proc.children(recursive=True)
                attempts -= 1

            if len(children) == 0:
                raise RuntimeError(t('started_process_without_gui'))

            return children

        proc = psutil.Popen(args, shell=shell, **kwargs)
        checked_processes = get_children(proc, attempts) if shell else [proc]

        while attempts:
            time.sleep(0.5)

            for proc in checked_processes:
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

    def is_exists(self, hwnd):
        _, _, code = run_command('wmctrl -l | grep {}'.format(self.__hwnd2hex(hwnd)))
        return code == 0

    def move(self, hwnd, x, y, width, height):
        borders = self.borders(hwnd)

        run_command('wmctrl -i -r {id} -b remove,maximized_vert,maximized_horz -e 0,{x},{y},{width},{height}'.format(
            id=hwnd,
            x=x + borders['left'],
            y=y + borders['top'],
            width=width - borders['left'] - borders['right'],
            height=height - borders['top'] - borders['bottom']
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
                    return last_opened.pop(), None

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
