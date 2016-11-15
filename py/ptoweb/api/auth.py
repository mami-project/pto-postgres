from functools import wraps
from ptoweb import app
from flask import request, Response

def require_auth(f):
  """
  Decorator for protecting API methods that should not be public.
  """

  #TODO: Dummy for now. Checks against a configurable ADMIN_KEY in the configuration
  #      file. To be extended when appropriate and necessary.

  @wraps(f)
  def decorated(*args, **kwargs):
    api_key = request.headers.get('X-API-KEY')
    if(api_key is None):
      api_key = request.args.get('apikey')
    print(api_key)
    if(api_key != app.config['ADMIN_KEY']):
      return Response("Authorization Required!", status=403, mimetype="text/palin")
    else:
      return f(*args, **kwargs)
  return decorated
