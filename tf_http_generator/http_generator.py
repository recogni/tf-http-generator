"""
Tensor generator that yields images and labels for the image.

Accepts HTTP POSTs which will enqueue data to the process queue.
"""
import threading
import time
import Queue
import json

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer   import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """ Custom HTTP server derives from ThreadingMixIn and HTTPServer.
    """
    pass


def MakePostHandler(postDataCb):
    """ Wrapper function to compose a HTTP Handler for the POSTs.

        The `postDataCb` will be invoked with the POST data, this will
        allow the app to enqueue data to its queue.
    """

    class CustomHandler(BaseHTTPRequestHandler):
        """ Custom HTTP handler to intercept and enqueue POST events.
        """
        def do_POST(self):
            """ POST handler.
            """
            length = int(self.headers['Content-Length'])
            data   = self.rfile.read(length)
            postDataCb(data)

            # Respond with a 200 - OK.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("OK")

    return CustomHandler


class TfHttpGenerator():
    """ Generator class to wrap the server and generator for TF.
    """
    queue   = None              # Opaque queue from app (fetch only)
    postFn  = None              # Post fn to invoke
    port    = None              # Server PORT #

    def __init__(self, q, pfn, port=8080):
        """ Custom HTTP generator.  Requires an argument which specifies
            the handler function to invoke which parses the JSON data
            and enqueues into the queue.
        """
        self.queue  = q
        self.postFn = pfn
        self.port   = port


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


    def run(self):
        server_addr = ("", self.port)
        posth       = MakePostHandler(self.postFn)
        httpd       = ThreadingHTTPServer(server_addr, posth)

        print("Server starting...")
        httpd.serve_forever()


    def run_threaded(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
