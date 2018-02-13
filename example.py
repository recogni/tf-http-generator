import tensorflow as tf
from tf_http_generator import TfHttpGenerator

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
        sess.run(op) # Yields (0,1)
        sess.run(op) # Yields (2,3)
        sess.run(op) # Yields (4,5)

        # Will wait here until a POST is made
        sess.run(op) # Yields (6,42)



if __name__ == "__main__":
    main()
