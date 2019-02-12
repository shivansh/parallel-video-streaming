# Parallel Video Streaming

This is a message-passing based rewrite of my [Networks
project](https://github.com/shivansh/videoStream), which was based on a (rather
complicated) multithreaded model. Refer the [blog
post](https://shivansh.github.io/posts/2019-01-09-Revisiting-networks-project/)
for details.

## Dependencies

- pika
- opencv

The current version is compatible with Python 2.7.15rc1.

## Instructions

Start the entities in the sequence mentioned below -
- rabbit-mq server
- server.py
- client.py

## Relevant links
- https://github.com/skvark/opencv-python/issues/46
