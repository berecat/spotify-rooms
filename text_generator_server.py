import logging

import grpc
from time import perf_counter
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, Executor

from text_generator_pb2 import GenerateRequest, GenerateStreamedRequest, GenerateResponse, GenerateStreamedResponse
from text_generator_pb2_grpc import TextGeneratorServicer, add_TextGeneratorServicer_to_server
from transformers import GPT2Tokenizer, GPT2LMHeadModel, PreTrainedTokenizer, PreTrainedModel, StoppingCriteriaList

# Max length of the generated sequence if the value is not provided in a request.
__DEFAULT_MAX_LENGTH = 20
# Number of seconds between intermediate results if other value is not provided in a request.
__DEFAULT_INTERMEDIATE_RESULT_INTERVAL_SECONDS = 1.0


class TextGenerator(TextGeneratorServicer):
    __executor: Executor
    __tokenizer: PreTrainedTokenizer
    __model: PreTrainedModel

    def __init__(self, executor: Executor, tokenizer: PreTrainedTokenizer, model: PreTrainedModel):
        self.__executor = executor
        self.__tokenizer = tokenizer
        self.__model = model

    # Generate text starting with the given text.
    def _generate_text(self, text: str, max_length: int = None, stopping_criteria: StoppingCriteriaList = None) -> str:
        global __DEFAULT_MAX_LENGTH
        inputs = self.__tokenizer.encode(text, return_tensors='pt')
        if max_length is None or max_length <= 0:
            max_length = __DEFAULT_MAX_LENGTH
        outputs = self.__model.generate(inputs, max_length=max_length, do_sample=True,
                                        stopping_criteria=stopping_criteria)
        return self.__tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Implementation of the TextGenerator.Generate RPC.
    def Generate(self, request: GenerateRequest, unused_context: grpc.aio.ServicerContext) -> GenerateResponse:
        logging.info("Request: %s", request.text)
        output_text = self._generate_text(request.text, max_length=request.max_length)
        return GenerateResponse(text=output_text)

    # Implementation of the TextGenerator.GenerateStreamed RPC.
    def GenerateStreamed(self, request: GenerateStreamedRequest,
                         unused_context: grpc.aio.ServicerContext) -> GenerateResponse:
        global __DEFAULT_INTERMEDIATE_RESULT_INTERVAL_SECONDS

        logging.info("Request for a stream: %s", request.text)

        # Queue to store intermediate and final results.
        result_queue = Queue()

        def generate():
            start_time = perf_counter()
            intermediate_result_interval_seconds = request.intermediate_result_interval_ms / 1000.0 \
                if request.intermediate_result_interval_ms > 0 else __DEFAULT_INTERMEDIATE_RESULT_INTERVAL_SECONDS
            result_text = ""

            # A fake stopping criteria. Decodes input_ids and put them to the results queue.
            def custom_stopping_criteria(input_ids, unused_scores) -> bool:
                nonlocal start_time, result_text
                current_time = perf_counter()
                # Check that the last intermediate result was sent not longer than intermediate_result_interval_seconds
                # seconds ago.
                if (current_time - start_time) >= intermediate_result_interval_seconds:
                    # Put the intermediate generation result into the current_text
                    current_text = self.__tokenizer.decode(input_ids[0], skip_special_tokens=True)
                    # Get the tail of the current_text as a next text fragment.
                    next_text_fragment = current_text[len(result_text):]
                    result_text = current_text

                    result_queue.put_nowait(next_text_fragment)
                    start_time = current_time
                # We don't want to affect any real stopping criteria, so always return False.
                return False

            try:
                current_text = self._generate_text(request.text, max_length=request.max_length,
                                                   stopping_criteria=StoppingCriteriaList([custom_stopping_criteria]))
                result_queue.put_nowait(current_text[len(result_text):])
            finally:
                # Put empty result as a token end of stream.
                result_queue.put_nowait(None)

        # Start the text generation routine in a thread.
        generate_future = self.__executor.submit(generate)

        r = result_queue.get()
        while r is not None:
            yield GenerateStreamedResponse(text_fragment=r)
            r = result_queue.get()

        # Read result to handle any possible thrown exceptions.
        generate_future.result()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Load "gpt2" model. Can be replaced with any other text-generating models.
    model_name = "gpt2"
    logging.info("Initializing model \"%s\"", model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained(model_name)

    text_generator = TextGenerator(ThreadPoolExecutor(max_workers=20), tokenizer, model)

    server = grpc.server(ThreadPoolExecutor(max_workers=20))
    add_TextGeneratorServicer_to_server(text_generator, server)

    listen_address = "[::]:50052"
    server.add_insecure_port(listen_address)
    logging.info("Starting server on %s", listen_address)
    server.start()
    server.wait_for_termination()
