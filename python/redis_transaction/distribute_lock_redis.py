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
                print('lock success'+self._lock_value+';'+str(time.time()))
                return self._lock_value
            time.sleep(1)

    def release(self):
        pipe = self._client.pipeline(True)
        while True:
            try:
                pipe.watch(self._lock_key)
                # value = pipe.get(self._lock_key)
                if pipe.get(self._lock_key).decode(encoding='utf-8') == self._lock_value:
                    pipe.multi()
                    pipe.delete(self._lock_key)
                    print('unlock success'+self._lock_value+';'+str(time.time()))
                    pipe.execute()
                    
                    return True
                pipe.unwatch()
                break
            except redis.exceptions.WatchError:
                pass
        return False

    def _make_redis_client(self, host, port):
        cache_connection_url = 'redis://{}:{}'.format(host, port) \
            if host is not None and port is not None else 'redis://localhost:6379'  
        connection_pool = redis.ConnectionPool.from_url(cache_connection_url)
        self._client = redis.StrictRedis(connection_pool=connection_pool, decode_responses=True)


def test_func():
    lock = RedisLock('test','localhost',6379)
    lock.acquire(timeout=10)
    time.sleep(3)
    lock.release() 

  
if __name__ == "__main__":
    # test_func()
    for i in range(5):
        p1 = multiprocessing.Process(name=str(i), target=test_func)
        p1.start()