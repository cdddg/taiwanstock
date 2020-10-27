import abc
from itertools import cycle


class ProxyProvider(abc.ABC):
    @abc.abstractmethod
    def get_proxy(self):
        return NotImplemented


class NoProxyProvier(ProxyProvider):
    def get_proxy(self):
        return {}


class SingleProxyProvider(ProxyProvider):
    def __init__(self, proxy=None):
        self._proxy = proxy

    def get_proxy(self):
        return self._proxy


class RoundRobinProxiesProvider(ProxyProvider):
    def __init__(self, proxies: list):
        self._proxies = proxies
        self._proxies_cycle = cycle(proxies)

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, proxies: list):
        if not isinstance(proxies, list):
            raise ValueError("Proxies only accept list")

        self._proxies = proxies
        self._proxies_cycle = cycle(proxies)

    def get_proxy(self):
        return next(self._proxies_cycle)
