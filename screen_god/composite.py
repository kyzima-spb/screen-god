# -*- coding: utf-8 -*-

from screen_god.manager import WindowManager
from screen_god.messages import _ as t


DEBUG_STR = '{:>12}: {}'


class AbstractItem(object):
    __instances = {}

    def __get_item_size(self, base_size):
        value, unit = self.size()

        if unit is None:
            item_count = self.layout().item_count()
            return int(value * base_size / item_count)

        if unit == '%':
            return int(value * base_size / 100)

        if unit == 'px':
            return value

    def __init__(self, size=1):
        self.__layout = None
        self.__next = None
        self.__prev = None
        self.__size = size
        self.__x = None
        self.__y = None
        self.__width = None
        self.__height = None

    def close(self):
        raise NotImplementedError(t('abstract_method', method='Item.close()'))

    def debug(self):
        print('\n'.join([
            DEBUG_STR.format('Размер', self.size()),
            DEBUG_STR.format('Ширина', self.width()),
            DEBUG_STR.format('Высота', self.height()),
            DEBUG_STR.format('Слева', self.x()),
            DEBUG_STR.format('Сверху', self.y()),
            ''
        ]))

    @classmethod
    def get_instance(cls, uid, *args, **kwargs):
        item = cls.__instances.get(uid)

        if item is None:
            item = cls(*args, **kwargs)
            cls.__instances[uid] = item

        return item

    def height(self, force=False):
        if not force and self.__height:
            return self.__height

        layout = self.layout()

        if layout.direction() == Layout.HORIZONTAL:
            self.__height = layout.height()
        else:
            self.__height = self.__get_item_size(layout.height())

        return self.__height

    def layout(self):
        return self.__layout

    def move(self):
        raise NotImplementedError(t('abstract_method', method='Item.move()'))

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
            raise TypeError(t('incompatible_type_argument', name='layout', type='Layout'))

        self.__layout = layout

    def set_next(self, item):
        if item and not isinstance(item, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='item', type='AbstractItem'))

        self.__next = item

    def set_prev(self, item):
        if item and not isinstance(item, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='item', type='AbstractItem'))

        self.__prev = item

    def set_x(self, x):
        if self.layout() is not None:
            raise RuntimeError(t('property_calculated_automatically'))

        self.__x = int(x)

    def set_y(self, y):
        if self.layout() is not None:
            raise RuntimeError(t('property_calculated_automatically'))

        self.__y = int(y)

    def set_width(self, width):
        if self.layout() is not None:
            raise RuntimeError('Use the Item.size() method for setting the element size.')

        self.__width = int(width)

    def size(self):
        size = self.__size or 1

        if isinstance(size, int):
            return size, None

        if isinstance(size, str):
            for i, c in enumerate(size):
                if not c.isdigit():
                    break

            return int(size[:i]), size[i:]

        raise ValueError('Unknown unit "{}".'.format(size))

    def width(self, force=False):
        if not force and self.__width:
            return self.__width

        layout = self.layout()

        if layout.direction() == Layout.VERTICAL:
            self.__width = layout.width()
        else:
            self.__width = self.__get_item_size(layout.width())

        return self.__width

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


class Item(AbstractItem):
    def __init__(self, wnd=None, select_by_click=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__hwnd = None

        if wnd or select_by_click:
            self.set_window(wnd, select_by_click)

    def close(self):
        pass

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

        raise ValueError(t('invalid_argument_value', name='cmd'))


class ProcessItem(AbstractItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__hwnd = None
        self.__proc = None

    def close(self):
        if self.__proc:
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


class Layout(AbstractItem):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    def __init__(self, direction, width=None, height=None, x=None, y=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__direction = direction
        self.__head = None
        self.__tail = None

        if x is not None:
            self.set_x(x)

        if y is not None:
            self.set_y(y)

        if width:
            self.set_width(width)

        if height:
            self.set_height(height)

    def __iter__(self):
        return LayoutIterator(self)

    def __do_insert_after(self, item, target):
        is_head = target.prev() is None

        if is_head:
            self.__head = item
        else:
            target.prev().set_next(item)
            item.set_prev(target.prev())

        item.set_next(target)
        target.set_prev(item)

    def __do_insert_before(self, item, target):
        is_tail = target.next() is None

        if is_tail:
            self.__tail = item
        else:
            target.next().set_prev(item)
            item.set_next(target.next())

        item.set_prev(target)
        target.set_next(item)

    def __insert(self, item, target=None, after=False):
        if not isinstance(item, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='item', type='AbstractItem'))

        self.validate(item)

        item.reset()
        item.set_layout(self)

        if self.__head is None:
            self.__head = item
            self.__tail = item
            return

        if not isinstance(target, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='target', type='AbstractItem'))

        self.__do_insert_after(item, target) if after else self.__do_insert_before(item, target)

    def append(self, item):
        return self.__insert(item, self.last(), after=False)

    def close(self):
        for item in self:
            item.close()

    def debug(self):
        print('\n'.join([
            DEBUG_STR.format('Тип', 'Слой')
        ]))

        super().debug()

        for item in self:
            item.debug()

    def direction(self):
        return self.__direction

    def first(self):
        return self.__head

    def insert_after(self, item, target):
        self.__insert(item, target, after=True)

    def insert_before(self, item, target):
        self.__insert(item, target, after=False)

    def item_count(self):
        count = 0

        for item in self:
            value, unit = item.size()

            if unit:
                break

            count += value

        return count

    def last(self):
        return self.__tail

    def move(self):
        for item in self:
            item.move()

    def remove(self, item):
        if not isinstance(item, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='item', type='AbstractItem'))

        if item.prev() is None:
            self.__head = item.next()
        else:
            item.prev().set_next(item.next())

        if item.next() is None:
            self.__tail = item.prev()
        else:
            item.next().set_prev(item.prev())

        item.reset()

    def validate(self, item, throw=True):
        if not isinstance(item, AbstractItem):
            raise TypeError(t('incompatible_type_argument', name='item', type='AbstractItem'))

        if self.last() is None:
            return True

        _, src_unit = self.last().size()
        _, unit = item.size()

        if unit != src_unit:
            if throw:
                raise RuntimeError(t('invalid_units', unit=unit, layout_unit=src_unit))
            return False

        return True


class LayoutIterator(object):
    def __init__(self, layout):
        if not isinstance(layout, Layout):
            raise TypeError(t('incompatible_type_argument', name='layout', type='Layout'))

        self.__start = layout.first()

    def __next__(self):
        return self.next()

    def next(self):
        if self.__start is None:
            raise StopIteration

        item = self.__start
        self.__start = item.next()

        return item
