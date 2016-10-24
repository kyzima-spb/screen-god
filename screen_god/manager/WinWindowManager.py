# -*- coding: utf-8 -*-

import time

import psutil
import win32api
import win32gui
import win32con
import win32process

from screen_god import t
from screen_god.manager.WindowManager import WindowManager


class WinWindowManager(WindowManager):
    def borders(self, hwnd):
        border = win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)

        return {
            'left': border,
            'right': border,
            'top': border,
            'bottom': border,
        }

        # print(win32gui.GetClientRect(hwnd))
        # print(win32gui.GetWindowRect(hwnd))

    def close(self, hwnd):
        win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_CLOSE, 0)

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
            }

    def get_opened(self):
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

        opened = self.get_opened()

        try:
            return super().Popen(*args, attempts=attempts, **kwargs)
        except psutil.NoSuchProcess:
            while attempts:
                last_opened = set(self.get_opened()) - set(opened)

                if len(last_opened):
                    return last_opened.pop(), None

                attempts -= 1
                time.sleep(0.5)

            raise RuntimeError(t('started_process_without_gui'))
