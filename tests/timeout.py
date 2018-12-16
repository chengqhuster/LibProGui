# coding=utf-8
import functools


def decorator_with_params(arg_of_decorator):  # 这里是装饰器的参数
    print(arg_of_decorator)

    # 最终被返回的函数
    def newdecorator(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            func(*args, **kwargs)
        return handle_args
    return newdecorator


@decorator_with_params("deco_args")
def foo3():
    print(5)
    pass

foo3()
# print(foo3.__name__)


def decorator_whith_params_and_func_args(arg_of_decorator):
    def handle_func(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            print("begin")
            res = func(*args, **kwargs)
            print("end")
            print(arg_of_decorator, func.__name__, args, kwargs)
            return res
        return handle_args
    return handle_func


@decorator_whith_params_and_func_args("123")
def foo4(a, b=2):
    print("Content")

rres = foo4(1, b=3)
print(foo4.__name__)
print(rres)
