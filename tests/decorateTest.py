from functools import wraps


def decorate_fxn(a_fun):
    @wraps(a_fun)  # 带参数的装饰器
    def magic_fxn(a):  # 包装带参数
        print('Do something before decorated fxn')
        a_fun(a)
        print('Do something after decorated fxn')
    return magic_fxn


@decorate_fxn
def origin_fxn(a):
    print('I am the original fxn', a)

origin_fxn(2)
print(origin_fxn.__name__)
