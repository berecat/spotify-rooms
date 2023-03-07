import logging

import grpc
from text_generator_pb2 import GenerateRequest
from text_generator_pb2_grpc import TextGeneratorStub


def run():
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = TextGeneratorStub(channel)
        response = stub.Generate(GenerateRequest(text='Here is a story about', max_length=150))
        print(response.text)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
