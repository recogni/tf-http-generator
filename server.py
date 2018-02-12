#!/usr/bin/env python

"""
Tensor generator that yields images and labels for the image.

Accepts HTTP POSTs which will enqueue data to the process queue.
"""
import threading
import time
import Queue

from sys import argv
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer   import ThreadingMixIn


""" Custom HTTP server derives from ThreadingMixIn and HTTPServer.
"""
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


""" App specific server handler.
"""
def MakePostHandler(queue):
    class Server(BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_POST(self):
            queue.put(123)
            self._set_headers()
            self.wfile.write("%d" % (123))

    return Server


""" Generator class to wrap the server and generator for TF.
"""
class TfHttpGenerator():
    queue = Queue.Queue()

    def enqueue(self, o):
        self.queue.put(o)

    def generator(self):
        # TODO: Check for keepalive flag.
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


"""

    This code is WIP - the below main() exists to validate the generator.

"""
def main():
    tfgen = TfHttpGenerator()
    gen   = tfgen.generator()

    # Start the server
    tfgen.run_threaded()

    # Stuff some items on queue
    tfgen.enqueue(10);
    tfgen.enqueue(11);
    tfgen.enqueue(12);
    tfgen.enqueue(13);

    for i in range(10):
        x = gen.next()
        print("GOT ITEM: %d" % x)

if __name__ == "__main__":
    main()
