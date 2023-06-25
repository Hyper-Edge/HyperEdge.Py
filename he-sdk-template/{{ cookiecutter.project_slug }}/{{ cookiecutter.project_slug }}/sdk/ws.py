import json
import pydantic
import sys
import multiprocessing
import threading
import websocket


class JobData(pydantic.BaseModel):
    job_id: str
    success: bool
    retval: object


def _get_ws_job_id(v):
    if not v:
        return None
    parts = v.split('.')
    return parts[1] if len(parts) == 2 else None


def _ws_listener(ws, queue: multiprocessing.Queue):
    while True:
        try:
            msg = ws.recv()
            if not msg:
                continue
            jmsg = json.loads(msg)
            if jmsg['event'] == 'message':
                job_id = _get_ws_job_id(jmsg.get('subscription'))
                if not job_id:
                    continue
                print(jmsg)
                is_success = jmsg['data'].get('status') == 'success'
                job_data = JobData(job_id=job_id, success=is_success, retval=jmsg['data'].get('retval'))
                print(job_data)
                queue.put(job_data)
        except websocket.WebSocketConnectionClosedException:
            # handle connection closed, probably break the loop
            print("Connection closed")
            sys.exit(0)
        except Exception as e:
            print("Other error occured. {}".format(e))
            sys.exit(0)


class HeWsClient(object):
    def __init__(self, url: str, ticket: str):
        self._url = url
        self._mgr = multiprocessing.Manager()
        self._queue = self._mgr.Queue()
        self._ws = websocket.create_connection(self._url)
        self._thread = threading.Thread(target=_ws_listener, args=(self._ws, self._queue,), daemon=True)
        self._thread.start()
        self._job_results = {}
        #
        self.auth(ticket)

    @property
    def url(self):
        return self._url

    def auth(self, ticket):
        self._ws.send(json.dumps({'event': 'auth', 'method': 'ticket', 'ticket': ticket}))

    def _subscribe_for_job(self, job_id):
        self._ws.send(json.dumps({"event": "subscribe", "subscription": f"jobs.{job_id}"}))

    def wait_for_job(self, job_id: str):
        self._subscribe_for_job(job_id)
        #
        job_data = self._job_results.get(job_id)
        while job_data is None:
            q_job_data = self._queue.get()
            self._job_results[q_job_data.job_id] = q_job_data
            job_data = self._job_results.get(job_id)
        return job_data
