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

import tensorflow as tf


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
            queue.put((123, "WORLD"))
            self._set_headers()
            self.wfile.write("%d" % (123))

    return Server


""" Generator class to wrap the server and generator for TF.
"""
class TfHttpGenerator():
    queue = Queue.Queue()

    def enqueue(self, v):
        self.queue.put((v, "HELLO"))

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

    # Start the server
    tfgen.run_threaded()

    dataset = tf.data.Dataset.from_generator(tfgen.generator, output_types=(tf.int32, tf.string))

    # Stuff some items on queue
    tfgen.enqueue(0);
    tfgen.enqueue(1);
    tfgen.enqueue(2);
    tfgen.enqueue(3);
    tfgen.enqueue(4);
    tfgen.enqueue(5);

    tfgen.enqueue(6);

    dataset = dataset.batch(2)
    iter = dataset.make_one_shot_iterator()

    x, y = iter.get_next()
    op = tf.Print(x, [x, y], "X,Y=")

    with tf.Session() as sess:
        while True:
            sess.run(op)


if __name__ == "__main__":
    main()
