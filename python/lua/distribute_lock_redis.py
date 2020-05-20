import redis
import uuid
import time
import multiprocessing


class RedisLock(object):
    def __init__(self, lock_key, redis_host='localhost', redis_port=6379):
        self._lock_value = str(uuid.uuid4())
        self._lock_key = "lock_{}".format(lock_key)
        self._client = None
        self._make_redis_client(redis_host, redis_port)

    def acquire(self, timeout=10):
        while True:
            value = self._client.set(self._lock_key, self._lock_value, nx=True, ex=timeout)
            if value:
                print('lock success')
                return self._lock_value
            time.sleep(1)

    def release(self):
        cmd = 'if redis.call("get",KEYS[1]) == ARGV[1] then\n    return redis.call("del",KEYS[1])\nelse\n    return 0\nend'
        exe = self._client.register_script(cmd)
        exe(keys=[self._lock_key], args=[self._lock_value])
        print('lock_failed')
        # old_value = self._client.get(self._lock_key)
        # if old_value == self._lock_value:
        #     return self._client.delete(self._lock_key)

    def _make_redis_client(self, host, port):
        cache_connection_url = 'redis://{}:{}'.format(host, port) \
            if host is not None and port is not None else 'redis://localhost:6379'  
        connection_pool = redis.ConnectionPool.from_url(cache_connection_url)
        self._client = redis.StrictRedis(connection_pool=connection_pool, decode_responses=True)

def test_func():
    lock = RedisLock('test','localhost',6987)
    lock.acquire(timeout=10)
    time.sleep(5)
    lock.release() 

  
if __name__ == "__main__":
    for i in range(10):
        p1 = multiprocessing.Process(name=str(i), target=test_func)
        p1.start()
    # test_func()