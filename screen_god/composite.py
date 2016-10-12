# -*- coding: utf-8 -*-

from screen_god.manager import WindowManager


DEBUG_STR = '{:>12}: {}'


class AbstractItem(object):
    def __get_item_size(self, raw_value, base_size):
        if isinstance(raw_value, int):
            item_count = self.layout().item_count()
            return int(raw_value * base_size / item_count)

        if isinstance(raw_value, str):
            if raw_value.endswith('%'):
                return int(raw_value.rstrip('%')) * base_size / 100

            if raw_value.endswith('px'):
                return int(raw_value.rstrip('px'))

        raise ValueError('Unknown unit "{}".'.format(raw_value))

    def __init__(self, size=1):
        self.__layout = None
        self.__next = None
        self.__prev = None
        self.__size = size
        self.__x = None
        self.__y = None
        self.__width = None
        self.__height = None

    def debug(self):
        print('\n'.join([
            DEBUG_STR.format('Размер', self.size()),
            DEBUG_STR.format('Ширина', self.width()),
            DEBUG_STR.format('Высота', self.height()),
            DEBUG_STR.format('Слева', self.x()),
            DEBUG_STR.format('Сверху', self.y()),
            ''
        ]))

    def height(self, force=False):
        if not force and self.__height:
            return self.__height

        layout = self.layout()

        if layout.direction() == Layout.HORIZONTAL:
            self.__height = layout.height()
        else:
            self.__height = self.__get_item_size(self.size(), layout.height())

        return self.__height

    def layout(self):
        return self.__layout

    def move(self):
        raise NotImplementedError('Item.execute() is abstract and must be overridden.')

    def next(self):
        return self.__next

    def prev(self):
        return self.__prev

    def reset(self):
        self.__layout = None
        self.__next = None
        self.__prev = None
        self.__x = None
        self.__y = None
        self.__width = None
        self.__height = None

    def set_height(self, height):
        if self.layout() is not None:
            raise RuntimeError('Use the Item.size() method for setting the element size.')

        self.__height = int(height)

    def set_layout(self, layout):
        if not isinstance(layout, Layout):
            raise TypeError('Passed argument is not a Layer.')

        self.__layout = layout

    def set_next(self, item):
        if not isinstance(item, AbstractItem):
            raise TypeError('Passed argument is not a Item.')

        self.__next = item

    def set_prev(self, item):
        if not isinstance(item, AbstractItem):
            raise TypeError('Passed argument is not a Item.')

        self.__prev = item

    def set_x(self, x):
        if self.layout() is not None:
            raise RuntimeError('The property will be calculated automatically.')

        self.__x = int(x)

    def set_y(self, y):
        if self.layout() is not None:
            raise RuntimeError('The property will be calculated automatically.')

        self.__y = int(y)

    def set_width(self, width):
        if self.layout() is not None:
            raise RuntimeError('Use the Item.size() method for setting the element size.')

        self.__width = int(width)

    def size(self):
        return self.__size or 1

    def x(self, force=False):
        if not force and self.__x is not None:
            return self.__x

        layout = self.layout()
        prev = self.prev()

        if prev is None or layout.direction() == Layout.VERTICAL:
            self.__x = layout.x()
            return self.__x

        self.__x = prev.x() + prev.width()

        return self.__x

    def y(self, force=False):
        if not force and self.__y is not None:
            return self.__y

        layout = self.layout()
        prev = self.prev()

        if prev is None or layout.direction() == Layout.HORIZONTAL:
            self.__y = layout.y()
            return self.__y

        self.__y = prev.y() + prev.height()

        return self.__y

    def width(self, force=False):
        if not force and self.__width:
            return self.__width

        layout = self.layout()

        if layout.direction() == Layout.VERTICAL:
            self.__width = layout.width()
        else:
            self.__width = self.__get_item_size(self.size(), layout.width())

        return self.__width


class Item(AbstractItem):
    def __init__(self, wnd=None, select_by_click=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__hwnd = None

        if wnd or select_by_click:
            self.set_window(wnd, select_by_click)

    def debug(self):
        print(DEBUG_STR.format('HWND', self.__hwnd))
        super().debug()

    def move(self):
        if self.__hwnd is None:
            raise RuntimeError('The window is not set')

        WindowManager.move(self.__hwnd, self.x(), self.y(), self.width(), self.height())

    def Popen(self, *args, **kwargs):
        hwnd, proc = WindowManager.Popen(*args, **kwargs)
        self.set_window(hwnd)

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

        raise ValueError('Invalid argument value "cmd".')


class Layout(AbstractItem):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    def __init__(self, direction, width=None, height=None, x=None, y=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__direction = direction
        self.__item_count = 0
        self.__first = None

        if x is not None:
            self.set_x(x)

        if y is not None:
            self.set_y(y)

        if width:
            self.set_width(width)

        if height:
            self.set_height(height)

    def __insert(self, item, target):
        if not isinstance(item, AbstractItem):
            raise TypeError('Passed argument is not a Item.')

        item.reset()

        if target.next():
            target.next().set_prev(item)
            item.set_next(target.next())

        item.set_prev(target)
        target.set_next(item)

        item.set_layout(self)
        self.__item_count += item.size()

    def append(self, item):
        if self.last():
            self.__insert(item, self.last())
        else:
            item.reset()
            self.__first = item
            item.set_layout(self)
            self.__item_count += item.size()

    def direction(self):
        return self.__direction

    def first(self):
        return self.__first

    def insert_after(self, item, target):
        self.__insert(item, target.prev())

    def item_count(self):
        return self.__item_count

    # def debug(self):
    #     super().debug()
    #
    #     for item in self.__items:
    #         print('\n')
    #         item.debug()

    def insert_before(self, item, target):
        self.__insert(item, target)

    def last(self):
        if self.first() is None:
            return None

        founded = self.first()

        while founded.next():
            founded = founded.next()

        return founded
