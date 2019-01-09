import cv2
import pika
import struct
import sys


class Server:

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs', exchange_type='fanout')

    def startWebcam(self):
        """Starts the stream and adjusts the screen resolution."""
        try:
            cap = cv2.VideoCapture(0)
            frame_width = 160
            frame_height = 120
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
            return cap
        except Exception as e:
            print(traceback.print_exc())

    def webcamFeed(self, cap):
        """Starts sending the webcam feed to the exchange"""
        print "Starting server..."
        try:
            while True:
                ret, frame = cap.read()
                payload = ""
                # Convert the frame into a byte string
                frame_dims = list(frame.shape)
                hashed_frame_dim = 0
                for dim in frame_dims:
                    hashed_frame_dim <<= 16
                    hashed_frame_dim += dim
                payload += struct.pack('Q', hashed_frame_dim) + frame.tobytes()
                self.channel.basic_publish(
                    exchange='logs', routing_key='', body=payload)

        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        self.connection.close()
        sys.exit("Exiting!")


def main():
    server = Server()
    cap = server.startWebcam()
    server.webcamFeed(cap)


if __name__ == '__main__':
    main()
