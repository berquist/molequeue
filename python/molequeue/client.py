import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
from utils import underscore_to_camelcase
from utils import JsonRpc
from threading import Thread
from threading import Condition
from threading import Lock
from functools import partial
import inspect
import json

class JobRequest:
  def __init__(self):
    self.queue = None
    self.program = None
    self.description = ''
    self.input_as_path = None
    self.input_as_string = None
    self.output_directory = None
    self.local_working_directory = None
    self.clean_remote_files = False
    self.retrieve_output = True
    self.clean_local_working_directory = False
    self.hide_from_gui = False
    self.pop_up_state_change = True

  def job_state(self):
    # TODO
    pass

  def molequeue_id(self):
    # TODO
    pass

  def queue_id(self):
    # TODO
    pass

class EventLoop(Thread):
  def __init__(self, io_loop):
    Thread.__init__(self)
    self.io_loop = io_loop

  def run(self):
    self.io_loop.start()

  def stop(self):
    self.io_loop.stop()

class MoleQueueException(Exception):
  """The base class of all MoleQueue exceptions """
  pass

class JobRequestException(MoleQueueException):
  def __init__(self, packet_id, code, message):
    self.packet_id = packet_id
    self.code = code
    self.message = message

class Client:

  def __init__(self):
    self._current_packet_id = 0
    self._request_response_map = {}
    self._new_response_condition = Condition()
    self._packet_id_lock = Lock()
    self._notification_callbacks = []

  def connect_to_server(self, server):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.DEALER)
    self.socket.connect('ipc://%s' % server)

    io_loop = ioloop.IOLoop(ioloop.ZMQPoller())

    self.stream = ZMQStream(self.socket, io_loop)

    # create partial function that has self as first argument
    callback = partial(_on_recv, self)
    self.stream.on_recv(callback)
    self.event_loop = EventLoop(io_loop)
    self.event_loop.start()

  def disconnect(self):
    self.stream.flush()
    self.event_loop.stop()
    self.socket.close()

  def register_notification_callback(self, callback):
    # check a valid function has been past
    assert not callback(callback)
    self._notification_callbacks.append(callback)

  def request_queue_list_update(self):
    pass

  def submit_job_request(self, request, timeout=None):
    params = {}
    for key, value in request.__dict__.iteritems():
      params[underscore_to_camelcase(key)] = value

    packet_id = self._next_packet_id()
    jsonrpc = JsonRpc.generate_request(packet_id,
                                      'submitJob',
                                      params)

    # add to request map so we know we are waiting on  response for this packet
    # id
    self._request_response_map[packet_id] = None
    self.stream.send(str(jsonrpc))
    self.stream.flush()

    # wait for the response to come in
    self._new_response_condition.acquire()
    while self._request_response_map[packet_id] == None:
      self._new_response_condition.wait(timeout)

    response = self._request_response_map[packet_id]
    self._new_response_condition.release()
    # if we an error occurred then throw an exception
    if 'error' in response:
      exception = JobRequestException(reponse['error']['id'],
                                      reponse['error']['code'],
                                      reponse['error']['message'])
      raise exception

    # otherwise return the molequeue id
    return response['result']['moleQueueId']

  def cancel_job(self):
    # TODO
    pass

  def lookup_job(self):
    # TODO
    pass

  def _on_response(self, packet_id, msg):
    if packet_id in self._request_response_map:
      self._new_response_condition.acquire()
      self._request_response_map[packet_id] = msg
      # notify any threads waiting that their response may have arrived
      self._new_response_condition.notify_all()
      self._new_response_condition.release()

  # TODO Convert raw JSON into a Python class
  def _on_notification(self, msg):
    for callback in self._notification_callbacks:
      callback(msg)

  def _next_packet_id(self):
    with self._packet_id_lock:
      self._current_packet_id += 1
      next = self._current_packet_id
    return next

def _on_recv(client, msg):
  jsonrpc = json.loads(msg[0])

  # reply to a request
  if 'id' in jsonrpc:
    packet_id = jsonrpc['id']
    client._on_response(packet_id, jsonrpc)
  # this is a notification
  else:
    client._on_notification(jsonrpc)