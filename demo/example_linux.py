# -*- coding: utf-8 -*-

import time

from screen_god import LauncherItem, Layout


designer = LauncherItem()
vlc = LauncherItem()
iceweasel = LauncherItem()

layout = Layout(direction=Layout.HORIZONTAL)
layout.append(designer)
layout.append(vlc)

main_layout = Layout(direction=Layout.VERTICAL, x=10, y=50, width=1400, height=900)
main_layout.append(layout)
main_layout.append(iceweasel)

designer.execute(['designer'])
vlc.execute(['vlc'])
iceweasel.execute(['iceweasel', '--private-window'])

main_layout.move()

time.sleep(3)

main_layout.close()
