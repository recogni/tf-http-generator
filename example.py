import Queue
import tensorflow as tf
from tf_http_generator import TfHttpGenerator

"""

    This code is WIP - the below main() exists to validate the generator.

"""
def customPostWrapper(queue):
    """ Wrapper to the app specific POST data handler.  This is so
        that we can give the dynamically invoked function access to
        the queue created by the app.
    """
    def func(data):
        # TODO (sabhiram) : Swap this with HTTP POST payload
        queue.put((42, "WORLD"))
        print("customPostHandler got :: %s" % data)

    return func


def main():
    # Queue that we want to populate in the `customPostHandler`
    queue = Queue.Queue()

    # Special server + generator for tensor batches.
    tfgen = TfHttpGenerator(queue, customPostWrapper(queue), port=8081)

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
    queue.put((0, "HELLO"));
    queue.put((1, "HELLO"));
    queue.put((2, "HELLO"));
    queue.put((3, "HELLO"));
    queue.put((4, "HELLO"));
    queue.put((5, "HELLO"));

    # This item does not have a pair to be part of a batch with yet.
    queue.put((6, "HELLO"));

    # Define the input and label (x and y for the dataset)
    x, y = iter.get_next()

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
