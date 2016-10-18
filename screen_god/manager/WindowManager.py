# -*- coding: utf-8 -*-

import time

import psutil

from screen_god.messages import t


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
