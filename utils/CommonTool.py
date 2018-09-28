#!/usr/bin/env python
# -*- coding:utf-8 -*-


class ConstValue(object):
    """ 封装出来的一个常量类。所有设置的属性都只能设置一次，多次设置会产生异常。属性名必须是大写字符串。
    usage:
        >>> ConstValue.PI = 3.1415926
        >>> ConstValue.PI = 3.2
        <ConstError>
        >>> ConstValue.year = 2018
        <ConstCastError>
    """

    class ConstError(TypeError):
        """ 定义修改值产生的异常。"""
        pass

    class ConstCastError(ConstError):
        """ 定义变量非大写字符串产生的异常。"""
        pass

    def __setter__(self, name, value):
        """ 重写__setter__方法，对属性名以及修改做限制产生异常。
        :param name: 属性名字，必须是大写字符串。
        :param value: 属性的值。
        """
        if name in self.__dict__:
            raise self.ConstError('Not allowed change const.{value}'.format(value=name))
        if isinstance(name, str):
            raise self.ConstCastError("The const name is not a string.")
        if not str(name).isupper():
            raise self.ConstCastError("Const's name is not all uppercase")
        self.__dict__[name] = value


def func_bound_comment(logger):
    """ 在函数前后增加分界注释的装饰器。"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info("")
            logger.info("start {0} ...".format(func.__name__))
            result = func(*args, **kwargs)
            logger.info("end {0} ...".format(func.__name__))
            logger.info("")
            return result
        return wrapper
    return decorator
