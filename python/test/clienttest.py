import unittest
from functools import partial

import molequeue

class TestClient(unittest.TestCase):

  def test_submit_job_request(self):
    client = molequeue.Client()
    client.connect_to_server('MoleQueue')

    job_request = molequeue.JobRequest()
    job_request.queue = 'salix'
    job_request.program = 'sleep (testing)'

    molequeue_id = client.submit_job_request(job_request)

    print "MoleQueue ID: ", molequeue_id

    self.assertTrue(isinstance(molequeue_id, int))

    client.disconnect()

  def test_notification_callback(self):
    client = molequeue.Client()
    client.connect_to_server('MoleQueue')

    self.callback_count = 0

    def callback_counter(testcase, msg):
      testcase.callback_count +=1

    callback = partial(callback_counter, self)

    client.register_notification_callback(callback)
    client.register_notification_callback(callback)

    job_request = molequeue.JobRequest()
    job_request.queue = 'salix'
    job_request.program = 'sleep (testing)'

    molequeue_id = client.submit_job_request(job_request)

    self.assertIs(self.callback_count, 2)

    client.disconnect()

if __name__ == '__main__':
    unittest.main()