import simplejson as json

import config


def send_json(response, obj, callback, error=False):
  # Sends JSON to client-side
  json_result = obj
  if isinstance(obj, (str, unicode)):
    json_result = json.loads(obj)
  json_result['error'] = 0 if not error else 1
  json_result = json.dumps(obj)
 
  response.headers['Content-Type'] = 'application/json'
  if callback:
    response.out.write('%s(%s)' % (callback, json_result))
  else:
    response.out.write(json_result)


def json_error(response, message, callback):
  # Sends error in JSON to client-side
  send_json(response, {'message': message}, callback, True)
