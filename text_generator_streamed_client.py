import logging

import grpc
from text_generator_pb2 import GenerateStreamedRequest
from text_generator_pb2_grpc import TextGeneratorStub


def run():
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = TextGeneratorStub(channel)
        response = stub.GenerateStreamed(
            GenerateStreamedRequest(text='Here is a story about', max_length=150, intermediate_result_interval_ms=500))
        for r in response:
            print(r.text_fragment, end="")
        print()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
