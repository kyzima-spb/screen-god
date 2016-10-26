# -*- coding: utf-8 -*-

import time

from screen_god import LauncherItem, Layout


notepad = LauncherItem()
regedit = LauncherItem()
explorer = LauncherItem()
paint = LauncherItem()

layout = Layout(direction=Layout.HORIZONTAL)
layout.append(notepad)
layout.append(regedit)

main_layout = Layout(direction=Layout.VERTICAL, x=10, y=20, width=800, height=600)
main_layout.append(explorer)
main_layout.append(layout)
main_layout.append(paint)

notepad.execute(['notepad'])
regedit.execute(['regedit'])
explorer.execute(['explorer'])
paint.execute(['%SystemRoot%\system32\mspaint.exe'], shell=True)

main_layout.move()

time.sleep(3)

main_layout.close()
