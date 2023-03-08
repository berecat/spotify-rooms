# Text-Generation Response Streaming with HuggingFace and pyTorch

A simple [GRPC](https://grpc.io/) Python service demonstrates streaming text-generation with
[HuggingFace](https://huggingface.co/) and [pyTorch](https://pytorch.org/).

## GRPC Service Description

The sample `TextGenerator` GRPC service provides two methods.

```protobuf
service TextGenerator {
  rpc Generate(GenerateRequest) returns (GenerateResponse) {}
  rpc GenerateStreamed(GenerateStreamedRequest) returns (stream GenerateStreamedResponse) {}
}
```

`Generate` RPC can be used to generate text by a given staring phrase (`GenerateRequest.text`) returning a final
result as soon as max number of tokens reached (`GenerateRequest.max_length`). `max_length` is an optional field. If not
provided the default value will be used.

```protobuf
message GenerateRequest {
  string text = 1;
  int32 max_length = 2;
}
```

Result contains the only field `GenerateResponse.text` holding the product of generation process.

```protobuf
message GenerateResponse {
  string text = 1;
}
```

`GenerateStreamed` RPC performs the same work but streaming intermediate results during the generation process.
Optional `GenerateStreamedRequest.intermediate_result_interval_ms` field specifies a minimal time span between intermediate
results. For instance, if the time interval is set to 500ms and a total generation process would take longer than this value,
every 500 ms an intermediate result returned.

```protobuf
message GenerateStreamedRequest {
  string text = 1;
  int32 max_length = 2;
  int32 intermediate_result_interval_ms = 3;
}
```

Each message in the response stream contains the only field `GenerateStreamedResponse.text_fragment` with a value of
next portion of the generated text. The final value could be calculated as a concatenation of all text fragments in the
same order there were received.

```protobuf
message GenerateStreamedResponse {
  string text_fragment = 1;
}
```

## Approach Overview

In this example the GPT2 model is used, but you're free to use any other text-generating model.

```python
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
```

In order to collect intermediate results it is suggested to use a fake stopping criteria.

```python
def custom_stopping_criteria(input_ids, scores) -> bool:
    return False
```

The first parameter `input_ids` contains intermediate result tokens, the `tokenizer` can be used to decode the tokens to
text.

```python
tokenizer.decode(input_ids[0], skip_special_tokens=True)
```

To start text-generation process we encode the text into tokens wrapped into pyTorch tensors, then invoke model
generation providing `custom_stopping_criteria`.

```python
inputs = tokenizer.encode("Let me say something", return_tensors='pt')
outputs = model.generate(inputs, max_length=7, do_sample=True, stopping_criteria=[custom_stopping_criteria])
```

Putting all together:

```python
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Encode input tokens.
inputs = tokenizer.encode("Let me say something", return_tensors='pt')


def custom_stopping_criteria(input_ids, unused_scores) -> bool:
    # Print intermediate result. 
    print(tokenizer.decode(input_ids[0], skip_special_tokens=True))
    return False


outputs = model.generate(inputs, max_length=7, do_sample=True, stopping_criteria=[custom_stopping_criteria])
# Print final result
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Running the Code

### Prerequests

You need to have `pyTorch` and `HuggingFace` installed. In order to run the service the `grpc` is also need to be
installed.

Please refer to the official installation instruction, but in general case the following `pip` command could be used:

```shell
pip install grpcio grpcio-tools torch transformers
```

### Starting the Server

```shell
python text_generator_server.py
```

### Starting the Simple Client

```shell
python text_generator_client.py
```

### Starting the Streaming Client

```shell
python text_generator_streamed_client.py
```

## Follow-ups

### Generate New Protos

New GRPC wrappers need to be regenerated if any changes to  `protos/text_generator.proto` were made.

```shell
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. protos/text_generator.proto
```

This command generates and overwrites the following files:

- `text_generator_pb.py`
- `text_generator_pb.pyi`
- `text_generator_pb_grpc.py`
