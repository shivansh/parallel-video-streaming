import cv2
import numpy as np
import pika
import struct
import sys


class Client:

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

        # For each connection, we declare a new queue which will be destroyed as
        # soon as the consumer dies.
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='logs', queue=queue_name)
        self.channel.basic_consume(self.callback, queue=queue_name, no_ack=True)

    def start(self):
        """Starts the client."""
        # Restrict the media-player window size to fit the screen.
        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.cleanup()

    def callback(self, ch, method, properties, body):
        """Triggered each time a message is received by the consumer."""
        payload_size = struct.calcsize('Q')
        packed_frame_dim = body[:payload_size]
        hashed_frame_dim = struct.unpack('Q', packed_frame_dim)[0]

        frame_dims, chunk_size = [], 1
        while hashed_frame_dim:
            dim = hashed_frame_dim & 0xFFFF
            frame_dims += [dim]
            hashed_frame_dim >>= 16
            chunk_size *= dim

        frame_dims.reverse()
        body = body[payload_size:]
        serialized_frame = body[:chunk_size]
        frame = np.fromstring(
            serialized_frame, dtype='uint8').reshape(frame_dims)
        cv2.imshow('frame', frame)

        # Ref: https://stackoverflow.com/a/39201163/5107319
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()

    def cleanup(self):
        cv2.destroyAllWindows()
        self.connection.close()
        sys.exit("Exiting!")


def main():
    client = Client()
    client.start()


if __name__ == '__main__':
    main()
