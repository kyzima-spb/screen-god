# -*- coding: utf-8 -*-

import psutil

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
