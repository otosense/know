"""To explore different architectures"""

from dataclasses import dataclass
from typing import (
    Callable,
    Mapping,
    Iterable,
    Any
)

from atypes import Slab, MyType
from i2.multi_object import FuncFanout, ContextFanout

from know.util import DictZip

# from creek.util import DictZip

FiltFunc = Callable[[Any], bool]

Service = MyType(
    'Consumer', Callable[[Slab], Any], doc='A function that will call slabs iteratively'
)
Name = str


def let_through(x):
    return x



# TODO: Default service(s) (e.g. data-safe prints?)
# TODO: Default slabs? (iterate through)
@dataclass
class WithSlabs:
    slabs: Iterable[Slab]
    services: Mapping[Name, Service]

    def __post_init__(self):
        if isinstance(self.services, FuncFanout):
            self.multi_service = self.services
        else:
            # TODO: Add capability (in FuncFanout) to get a mix of (un)named consumers
            self.multi_service = FuncFanout(**self.services)
        self.slabs_and_services_context = ContextFanout(
            slabs=self.slabs, **self.multi_service
        )

    def __iter__(self):
        with self.slabs_and_services_context:
            # while True:
            #     slab = next(self.slabs)
            #     yield self.multi_service(slab)
            for slab in self.slabs:
                yield self.multi_service(slab)

    def __call__(self, callback: Callable = None, sentinel_func: FiltFunc = None):
        for multi_service_output in self:
            if callback:
                callback_output = callback(multi_service_output)
                if sentinel_func:
                    if sentinel_func(callback_output):
                        break


def test_multi_iterator():
    # get_multi_iterable = lambda: MultiIterable(
    #     audio=iter([1, 2, 3]), keyboard=iter([4, 5, 6])
    # )

    def is_none(x):
        return x is None

    def is_not_none(x):
        return x is not None

    # Note: Equivalent to any_non_none_value = Pipe(methodcaller('values'), iterize(
    # is_not_none), any)
    def any_non_none_value(d: dict):
        """True if and only if d has any non-None values

        >>> assert not any_non_none_value({'a': None, 'b': None})
        >>> assert any_non_none_value({'a': None, 'b': 3})
        """
        return any(map(is_not_none, d.values()))

    # Note: Does not work (never stops)
    # get_multi_iterable = lambda: MultiIterable(
    #     audio=iter([1, 2, 3]),
    #     keyboard=iter([4, 5, 6])
    # )

    slabs = DictZip(audio=iter([1, 2, 3]), keyboard=iter([4, 5, 6]))
    services = {'let_through': let_through, 'log': print}
    app = WithSlabs(slabs=slabs, services=services)

    assert list(app) == [
        {'audio': 1, 'keyboard': 4},
        {'audio': 2, 'keyboard': 5},
        {'audio': 3, 'keyboard': 6},
    ]
