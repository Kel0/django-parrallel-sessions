from typing import Optional

from redis import Redis


def get_redis_client(socket_path: str = "/tmp/redis.sock"):
    return Redis(decode_responses=True, unix_socket_path=socket_path)


class FSMContext:
    def __init__(
        self, redis_client: Optional[Redis] = None, socket_path: Optional[str] = None
    ):
        socket_path = "/tmp/redis.sock" if socket_path is None else socket_path
        self.redis_client = (
            redis_client if redis_client else get_redis_client(socket_path=socket_path)
        )

    def get(self, cache_key):
        return self.redis_client.get(cache_key)

    def set(self, cache_key, value):
        self.redis_client.set(cache_key, value=value)

    def set_by_generator(self):
        pass
