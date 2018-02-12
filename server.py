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
    # Special server + generator for tensor batches.
    tfgen = TfHttpGenerator()

    # Start the server (runs forever on another thread until the parent
    # class is destructed).
    tfgen.run_threaded()

    # Create a dataset from the generator fn. Define what the outputs should
    # look like.
    dataset = tf.data.Dataset.from_generator(tfgen.generator, output_types=(tf.int32, tf.string))

    # Define batch size
    dataset = dataset.batch(2)
    iter = dataset.make_one_shot_iterator()

    # Stuff some items on queue - Since we are making a batch size of 2,
    # only the first 3 pairs below will get pulled into the batch. At this
    # point the generator will stall.
    # To continue the session, submit a HTTP post to the server
    #       curl -d '{}' -X POST http://localhost:8080
    # This will enqueue an item onto the generator queue (for now the value
    # is a fixed int32 and a fixed string).
    tfgen.enqueue(0);
    tfgen.enqueue(1);
    tfgen.enqueue(2);
    tfgen.enqueue(3);
    tfgen.enqueue(4);
    tfgen.enqueue(5);

    # This item does not have a pair to be part of a batch with yet.
    tfgen.enqueue(6);

    # Define the input and label (x and y for the dataset)
    x, y = iter.get_next()

    # Define a print op so we can "process" them.
    op = tf.Print(x, [x, y], "X,Y=")

    # Run the session.
    with tf.Session() as sess:
        while True:
            sess.run(op)


if __name__ == "__main__":
    main()
