# tf-http-generator

A tensor generator that accepts data sent via HTTP POSTs.

## Idea

Dataset providers typically read a list of files and parse them or list all files and directories in a specified dataset directory.  These methods while adequate for pre-baked datasets, do not scale nicely to allow streaming of training data from various sources.

## Implementation

This library implements a tf generator which hides a HTTP server that is accepting images being POST'd.  The server will build a local queue of images that have not been pulled for training, as the iterator fetches tensors from the generator, items are removed from the `queue`.

## TODO

1. Queue can be in-memory at first, can move to disk if needed
