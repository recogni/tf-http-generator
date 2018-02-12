"""
Tensor generator that yields images and labels for the image.

Accepts HTTP POSTs which will enqueue data to the process queue.
"""
import threading
import time
import Queue

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer   import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """ Custom HTTP server derives from ThreadingMixIn and HTTPServer.
    """
    pass


def MakePostHandler(queue):
    """ Wrapper function to compose a HTTP Handler for the POSTs but
        one which has access to the invoking classes queues.
    """

    class CustomHandler(BaseHTTPRequestHandler):
        """ Custom HTTP handler to intercept and enqueue POST events.
        """

        def _set_headers(self):
            """ Sets required HTTP headers for success and sets up the
                content type for any data written to self.wfile.
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_POST(self):
            """ POST handler.
            """
            # TODO (sabhiram) : Fetch POST body and parse here
            # TODO (sabhiram) : Swap this with HTTP POST payload
            queue.put((123, "WORLD"))
            self._set_headers()

            # TODO (sabhiram) : Swap this with standard 200 response
            self.wfile.write("%d" % (123))

    return CustomHandler


class TfHttpGenerator():
    """ Generator class to wrap the server and generator for TF.
    """

    queue = Queue.Queue()               # Application global queue


    def enqueue(self, v):
        """ TEMPORARY helper function to enqueue tuples into the queue.
        """
        self.queue.put((v, "HELLO"))


    def generator(self):
        """ generator function for the dataset.  This will yield a tuple
            of image data and label on calls to the dataset iterator's
            get_next() method.
        """
        # TODO (sabhiram) : Figure out correct time to sleep, do we need a warning?
        while True:
            if self.queue.empty():
                print("Generator empty - waiting for more POST data")
                time.sleep(1)
                continue
            while not self.queue.empty():
                yield self.queue.get()

    def run(self, port=8080):
        print("Server starting...")
        server_addr = ("", port)
        httpd = ThreadingHTTPServer(server_addr, MakePostHandler(self.queue))
        httpd.serve_forever()

    def run_threaded(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
