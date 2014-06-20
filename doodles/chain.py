#!/usr/bin/env python
# encoding: utf-8
"""
Function chaining experiment.
"""

from collections import namedtuple


User = namedtuple('User', 'name email is_active')


def chain_recursive(seq):
    def cocoon(xs):
        def caterpillar(f=None, *args):
            if f:
                return cocoon(f(*(list(args) + [xs])))
            else:
                return xs

        return caterpillar

    return cocoon(seq)


def chain_iterative(seq, *args):
    for a in args:
        if isinstance(a, tuple):
            f = lambda xs: a[0](*(list(a[1:]) + [xs]))
        else:
            f = a

        seq = f(seq)

    return seq


class Chainable:
    def __init__(self, obj, *scopes, **kwargs):
        self.base = obj
        self.scopes = scopes
        self.original_scopes = kwargs.get('original_scopes', scopes)

    def __getattr__(self, name):
        # look for 'name' in scopes
        new_scope = None
        for s in self.scopes:
            if hasattr(s, '__getitem__'):
                try:
                    new_scope = s[name]
                except KeyError:
                    pass
            else:
                try:
                    new_scope = getattr(s, name, None)
                except:
                    pass

            if new_scope:
                break

        if not new_scope:
            new_scope = getattr(self.base, name, None)

        if not new_scope:
            raise AttributeError

        return Chainable(self.base, new_scope,
                         original_scopes=self.original_scopes)

    def __call__(self, *args):
        fargs = args + (self.base,)
        rv = self.scopes[0](*fargs)
        return Chainable(rv, *(self.original_scopes or self.scope))


def _main():
    # Get email domains of active users ("gmail.com" and "rodriguez.name").
    # Try different approaches.

    users = [
        User("Fry", "fry@gmail.com", True),
        User("Leela", "leela@gmail.com", True),
        User("Bender", "bender@rodriguez.name", True),
        User("Zoidberg", "john@zoidberg.name", False),
    ]

    # 1. Idiomatic
    print set(x.email.split('@')[-1] for x in users if x.is_active)

    # 2. Functional, hard to read
    print set(map(lambda x: x.email.split('@')[-1],
                  filter(lambda x: x.is_active, users)))

    # 3. Functional with unpythonic formatting, easy(?) to read backwards
    print set(
          map(   lambda x: x.email.split('@')[-1],
          filter(lambda x: x.is_active,
          users)))

    # 4. Functional, easy to read forward, chained using recursive
    #    implementation
    print chain_recursive(users) \
        (filter, lambda x: x.is_active) \
        (map,    lambda x: x.email.split('@')[-1]) \
        (set) \
        ()

    # 5. Functional, easy to read forward, chained using iterative
    #    implementation
    print chain_iterative(users,
        (filter, lambda x: x.is_active),
        (map,    lambda x: x.email.split('@')[-1]),
        set)

    # 6. Javascript style OOP with dynamic methods
    print Chainable(users, __builtins__) \
        .filter(lambda x: x.is_active) \
        .map(lambda x: x.email.split('@')[-1]) \
        .set() \
        .base

    class A:
        def derp(self, x): return map(lambda x: x.email.split('@')[-1], x)
    a = A()

    print Chainable(users, __builtins__, locals()) \
        .filter(lambda x: x.is_active) \
        .a.derp() \
        .set() \
        .base


if __name__ == '__main__':
    _main()
