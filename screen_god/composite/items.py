# -*- coding: utf-8 -*-

from time import sleep
from subprocess import PIPE
from threading import Thread

import psutil
from psutil import pid_exists

from screen_god.composite.base import DEBUG_STR, AbstractItem
from screen_god.manager import WindowManager
from screen_god.messages import t


class Item(AbstractItem):
    def __init__(self, wnd=None, select_by_click=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__hwnd = None

        if wnd or select_by_click:
            self.set_window(wnd, select_by_click)

    def hwnd(self):
        return self.__hwnd

    def close(self):
        WindowManager.close(self.hwnd())

    def debug(self):
        print('\n'.join([
            DEBUG_STR.format('Тип', 'Элемент'),
            DEBUG_STR.format('HWND', self.__hwnd)
        ]))
        super().debug()

    def move(self):
        if self.__hwnd is None:
            raise RuntimeError(t('window_not_set'))

        WindowManager.move(self.__hwnd, self.x(), self.y(), self.width(), self.height())

    def set_window(self, wnd, select_by_click=False):
        if isinstance(wnd, int):
            self.__hwnd = wnd if WindowManager.is_exists(wnd) else WindowManager.find_by_pid(wnd)
            return

        if isinstance(wnd, str):
            self.__hwnd = WindowManager.find_by_title(wnd)
            return

        if select_by_click:
            self.__hwnd = WindowManager.find_by_mouse_click()
            return

        raise ValueError(t('invalid_argument_value', name='wnd'))


class ProcessItem(AbstractItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__hwnd = None
        self.__proc = None

    def close(self):
        if self.__proc and psutil.pid_exists(self.__proc.pid):
            self.__proc.terminate()
            self.__hwnd = None
            self.__proc = None

    def debug(self):
        print(DEBUG_STR.format('Тип', 'Процесс'))
        print(DEBUG_STR.format('HWND', self.__hwnd))
        print(DEBUG_STR.format('Процесс', self.__proc))
        super().debug()

    def move(self):
        if self.__hwnd:
            WindowManager.move(self.__hwnd, self.x(), self.y(), self.width(), self.height())

    def Popen(self, *args, **kwargs):
        self.__hwnd, self.__proc = WindowManager.Popen(*args, **kwargs)
        return self.__hwnd, self.__proc


class LauncherItem(AbstractItem):
    def __init__(self, size=1, stdout_handler=None, stderr_handler=None, **kwargs):
        super(LauncherItem, self).__init__(size)

        self.__hwnd = None
        self.__proc = None
        self.__thread = None

        # self.__cmd = cmd
        self.__stdout_handler = stdout_handler
        self.__stderr_handler = stderr_handler

        if stdout_handler:
            kwargs['stdout'] = PIPE

        if stderr_handler:
            kwargs['stderr'] = PIPE

        self.__kwargs = kwargs

    def close(self):
        if self.__proc and pid_exists(self.__proc.pid):
            for proc in self.__proc.children(recursive=True):
                proc.terminate()

            self.__proc.terminate()

        self.__hwnd = None
        self.__proc = None
        self.__thread = None

    def debug(self):
        print('\n'.join([
            DEBUG_STR.format('Тип', 'Процесс'),
            DEBUG_STR.format('HWND', self.__hwnd),
            DEBUG_STR.format('Процесс', self.__proc)
        ]))
        super().debug()

    def execute(self, cmd):
        if self.__proc:
            return

        # self.__proc = psutil.Popen(cmd, **self.__kwargs)
        self.__hwnd, self.__proc = WindowManager.Popen(cmd, **self.__kwargs)
        self.move()

        if self.__stdout_handler:
            stdout_handler = self.__stdout_handler()

            self.__thread = Thread(target=self.reader, args=(self.__proc.stdout, stdout_handler))
            self.__thread.start()

    def move(self):
        if self.__hwnd:
            WindowManager.move(self.__hwnd, self.x(), self.y(), self.width(), self.height())

    def reader(self, std_thread, handler):
        while True:
            line = std_thread.readline()

            if not line:
                return

            line = line.rstrip()
            handler.execute(line)
            sleep(0.1)

        self.__thread.join()
