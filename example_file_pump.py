import Queue
import json
import base64

import numpy as np
import tensorflow as tf
from tensorflow.python.framework import dtypes
from tf_http_generator import TfHttpGenerator

"""

    This code is WIP - the below main() exists to validate the generator.

    Expects that there is a `tf-file-pump` running on the other end
    streaming files to us.

"""
def customPostWrapper(queue):
    """ Wrapper to the app specific POST data handler.  This is so
        that we can give the dynamically invoked function access to
        the queue created by the app.
    """
    def func(data):
        # TODO (sabhiram) : Swap this with HTTP POST payload
        o = json.loads(data)
        if o["ImageFileName"]:
            with open(o["ImageFileName"], "w") as fout:
                bs = base64.b64decode(o["ImageData"])
                b  = bytearray()
                b.extend(bs)
                queue.put((b, "LABEL"))
    return func


def main():
    # Queue that we want to populate in the `customPostHandler`
    queue = Queue.Queue()

    # Special server + generator for tensor batches.
    tfgen = TfHttpGenerator(queue, customPostWrapper(queue), port=8080)

    # Start the server (runs forever on another thread until the parent
    # class is destructed).
    tfgen.run_threaded()

    # Create a dataset from the generator fn. Define what the outputs should
    # look like.
    dataset = tf.data.Dataset.from_generator(
        tfgen.generator,
        output_types=(tf.uint8, tf.string))

    # Define batch size
    dataset = dataset.batch(2)
    iter = dataset.make_one_shot_iterator()

    # Define the input and label (x and y for the dataset)
    x, y = iter.get_next()
    print(x, y)

    # Define a print op so we can "process" them.
    op = tf.Print(x, [x, y], "X,Y=")

    # Run the session.
    with tf.Session() as sess:
        sess.run(op) # Yields (0,1)
        sess.run(op) # Yields (2,3)
        sess.run(op) # Yields (4,5)

        # Will wait here until a POST is made
        sess.run(op) # Yields (6,42)


if __name__ == "__main__":
    main()
