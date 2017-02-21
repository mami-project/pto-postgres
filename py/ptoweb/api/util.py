from ptoweb import cache

def get_from_cache(key):
  return cache.get(key)


def put_to_cache(key, value, timeout = 60 * 60):
  cache.set(key, value, timeout = timeout)
