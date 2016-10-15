# -*- coding: utf-8 -*-

__messages = {
    'abstract_method': '{method} is abstract and must be overridden.',
    'incompatible_type_argument': 'Incompatible type of the argument "{name}". Expected type "{type}".',
    'invalid_argument_value': 'Invalid argument value "{name}".',
    'invalid_units': 'Invalid units - "{unit}". Layout uses "{layout_unit}".',
    'property_calculated_automatically': 'The property will be calculated automatically.',
    'started_process_without_gui': 'You have started the process without a GUI.',
    'window_not_set': 'The window is not set.',
}


def t(msg, *args, **kwargs):
    msg = __messages.get(msg)
    return msg.format(*args, **kwargs) if msg else ''
