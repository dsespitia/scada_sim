#!/usr/bin/env python

"""
- Helper functions to read from/write to the datastore
- ***NOTE***: Read/write wrapper functions only support when
ModbusServerContext is setup with single=True
  - Will be looking at implementing to allow for single=False
- Datastore is broken down into the following:
  - di - discrete input - read only, boolean - 2
  - co - coil output - read and write, boolean - 1
  - hr - holding register - read and write - 3
  - ir - input register - read only - 4
"""


def read_di_register(context, slave_id, addr, count):
    return context.getValues(2, addr, count)


def read_co_register(context, slave_id, addr, count):
    return context.getValues(1, addr, count)


def write_co_register(context, slave_id, addr, values):
    return context.setValues(1, addr, values)


def read_hr_register(context, slave_id, addr, count):
    return context.getValues(3, addr, count)


def write_hr_register(context, slave_id, addr, values):
    return context.setValues(3, addr, values)


def read_ir_register(context, slave_id, addr, count):
    return context.getValues(4, addr, count)
