import pdb
import app.common.file_reading_util as file_reading_util
import boto3
import json
from botocore.exceptions import ClientError
import textwrap

def generate(file_context, system_info, prompt, starting_text='', model_id='meta.llama3-1-70b-instruct-v1:0'):

    session = boto3.Session()
    client = session.client("bedrock-runtime", region_name="us-west-2")
    # these seem to support on-demand inference
    # meta.llama2-13b-chat-v1
    # meta.llama2-70b-chat-v1
    # meta.llama3-8b-instruct-v1:0
    # meta.llama3-70b-instruct-v1:0
    # meta.llama3-1-8b-instruct-v1:0
    # meta.llama3-1-70b-instruct-v1:0
    # meta.llama3-1-405b-instruct-v1:0

    # this one doesn't support on-demand inference
    # meta.llama3-2-90b-instruct-v1:0

    # it seems like I may need to drop to the native format to specify system info

    # Define the conversation like below according to https://www.llama.com/docs/model-cards-and-prompt-formats/meta-llama-3/
    # <|begin_of_text|>
    # <|start_header_id|>system<|end_header_id|>
    #
    # You are a helpful AI assistant for travel tips and recommendations<|eot_id|>
    # <|start_header_id|>user<|end_header_id|>
    #
    # What can you help me with?<|eot_id|>
    # <|start_header_id|>assistant<|end_header_id|>

    # <|start_header_id|>assistant<|end_header_id|>: Ends with the assistant header, to prompt the model to start generation.
    # Following this prompt, Llama 3 completes it by generating the {{assistant_message}}.
    # It signals the end of the {{assistant_message}} by generating the <|eot_id|>.

    # To add additional history, you need to include the previous user and assistant turns and then ending with assistant
    # like below as the last message.

    full_text_prompt = prompt + '\n\n' + file_context
    formatted_prompt = textwrap.dedent(f"""
        <|begin_of_text|>
        <|start_header_id|>system<|end_header_id|>

        {system_info}<|eot_id|>
        <|start_header_id|>user<|end_header_id|>

        {full_text_prompt}<|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
""")

    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 2048,
        "temperature": 0.5,
        "top_p": 0.9
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        streaming_response = client.invoke_model_with_response_stream(
            modelId=model_id, body=request
        )

        # the temp_chunk and accum are used to accumulate the chunks so that it updates about
        # every 30 characters or so, instead of overly frequently
        temp_chunk = ''
        accum = starting_text
        llama_only_output = ''

        # Extract and print the streamed response text in real-time.
        for event in streaming_response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "generation" in chunk:
                text_chunk = chunk["generation"]

                temp_chunk += text_chunk

                if len(temp_chunk) > 30:
                    accum += temp_chunk
                    llama_only_output += temp_chunk
                    temp_chunk = ''
                    yield accum, accum, 'Running Llama generation'

        if temp_chunk:
            accum += temp_chunk
            llama_only_output += temp_chunk
        yield accum, accum, 'Finished Llama generation'

        return llama_only_output, accum

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        yield '', '', f"ERROR: Can't invoke '{model_id}'. Reason: {e}"
        return f"ERROR: Can't invoke '{model_id}'. Reason: {e}", f"ERROR: Can't invoke '{model_id}'. Reason: {e}", 'Error'
