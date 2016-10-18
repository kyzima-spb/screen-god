# -*- coding: utf-8 -*-

import time

from screen_god import ProcessItem, Layout


designer = ProcessItem()
vlc = ProcessItem()
iceweasel = ProcessItem()

layout = Layout(direction=Layout.HORIZONTAL)
layout.append(designer)
layout.append(vlc)

main_layout = Layout(direction=Layout.VERTICAL, x=10, y=50, width=1400, height=900)
main_layout.append(layout)
main_layout.append(iceweasel)

designer.Popen(['designer'])
vlc.Popen(['vlc'])
iceweasel.Popen(['iceweasel', '--private-window'])

main_layout.move()

time.sleep(3)

main_layout.close()
