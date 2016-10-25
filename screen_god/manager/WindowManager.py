# -*- coding: utf-8 -*-

import os.path as Path
from time import sleep

import psutil

from screen_god.messages import t


class NoSuchWindowException(Exception):
    """
    Exception raised when a window with a certain PID doesn't or no longer exists.
    """
    def __init__(self, msg=''):
        self.msg = msg

    def __repr__(self):
        ret = "%s.%s %s" % (self.__class__.__module__,
                            self.__class__.__name__, self.msg)
        return ret.strip()

    __str__ = __repr__


class WindowManager(object):
    def borders(self, hwnd):
        """Возвращает размеры декорации окна."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.borders()'))

    def close(self, hwnd):
        """Закрыть указанное окно."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.close()'))

    def find_by_pid(self, pid):
        """Найти окно по идентификатору процесса."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.find_by_pid()'))

    def find_by_title(self, title):
        """Найти окно по заголовку, используется точное совпадение."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.find_by_title()'))

    def geometry(self, hwnd):
        """Возвращает позицию и размеры окна относительно экрана."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.geometry()'))

    def get_last_opened(self, opened, attempts=10):
        """
        Возвращает окна, открытые после переданных в аргументе opened.
        Каждая попытка выполняется раз в половину секунды.
        """

        opened = set(opened)

        while attempts:
            last_opened = set(self.get_opened()) - opened

            if len(last_opened):
                return last_opened

            attempts -= 1
            sleep(0.5)

        return set()

    def get_opened(self):
        """Get all the open windows."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.get_opened()'))

    def get_pid_by_hwnd(self, hwnd):
        raise NotImplementedError(t('abstract_method', method='WindowManager.get_pid_by_hwnd()'))

    def is_exists(self, hwnd):
        """Возвращает True, если окно с указанным идентификатором существует."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.is_exists()'))

    def move(self, hwnd, x, y, width, height):
        """Изменяет размеры окна и перемещает его в указанную позицию."""
        raise NotImplementedError(t('abstract_method', method='WindowManager.move()'))

    def Popen(self, cargs, attempts=10, shell=False, **kwargs):
        opened = self.get_opened()
        proc = psutil.Popen(cargs, shell=shell, **kwargs)
        cmd = ' '.join(proc.cmdline())

        last_opened = self.get_last_opened(opened, attempts)

        if not len(last_opened):
            raise NoSuchWindowException(t('started_process_without_gui'))

        def f(p, cmd):
            name = Path.basename(' '.join(p.cmdline()))
            return cmd.find(name) != -1

        for hwnd in last_opened:
            pid = self.get_pid_by_hwnd(hwnd)
            p = psutil.Process(pid)

            if shell:
                if psutil.pid_exists(proc.pid):
                    for child in proc.children():
                        if child.pid == p.pid:
                            return hwnd, proc

                if f(p, cmd):
                    return hwnd, None
            else:
                if pid == proc.pid:
                    return hwnd, proc

                if p.name() == proc.name():
                    return hwnd, None

        raise NoSuchWindowException(t('started_process_without_gui'))
