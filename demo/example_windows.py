# -*- coding: utf-8 -*-

import time

from screen_god import ProcessItem, Layout


notepad = ProcessItem()
regedit = ProcessItem()
explorer = ProcessItem()
paint = ProcessItem()

layout = Layout(direction=Layout.HORIZONTAL)
layout.append(notepad)
layout.append(regedit)

main_layout = Layout(direction=Layout.VERTICAL, x=10, y=20, width=800, height=600)
main_layout.append(explorer)
main_layout.append(layout)
main_layout.append(paint)

notepad.Popen(['notepad'])
regedit.Popen(['regedit'])
explorer.Popen(['explorer'])
paint.Popen(['%SystemRoot%\system32\mspaint.exe'], shell=True)

main_layout.move()

time.sleep(3)

main_layout.close()
