import os

from openai import OpenAI, types

client: OpenAI
locator_id: str
journaller_id: str

def openai_init():
    global client
    global locator_id
    global journaller_id
    client = OpenAI()
    print('Client created')
    locator_id = os.environ.get('OPENAI_LOCATOR_ID')
    journaller_id = os.getenv('OPENAI_JOURNALLER_ID')

def create_thread() -> str:
    return client.beta.threads.create().id

def message_journaller(thread_id: str, user: str, image, caption: str) -> str:
    file = client.files.create(
        file=image,
        purpose="vision"
    )
    print(file.id)
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=[
            {
                "type": "text",
                "text": caption
            },
            {
                "type": "image_file",
                "image_file": { "file_id": file.id, "detail": "low"}
            }
        ]
    )
    res: str = get_response(thread_id=thread_id, user=user, assistant=journaller_id, instruction=journaller_instruction)
    return res

def message_locator(thread_id: str, user: str, content: str) -> str:
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return get_response(thread_id=thread_id, user=user, assistant=locator_id, instruction=locator_instruction)


def get_response(thread_id: str, user: str, assistant: str, instruction) -> str:
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant,
        instructions=f"Address the user as {user}. {instruction}"
    )

    if run.status == 'completed':
        messages = list(client.beta.threads.messages.list(thread_id=thread_id,run_id=run.id))
        print(f"Prompt Tokens = {run.usage.prompt_tokens}, Completion Tokens = {run.usage.completion_tokens}")
        return messages[0].content[0].text.value
    else:
        print(run.status)
        print(run.last_error)
    return "Sorry, I could not get that. Please try again! 🥲"

def delete_files():
    ls = client.files.list()
    for f in ls:
        client.files.delete(f.id)
    

locator_instruction = "Provide the user with spots/trails/places to view nature based on a given location, or landscapes that combine human and natural features. Alternatively, help the user with his journalling by providing feedback or follow up questions. Deny any messages that do not talk about nature, locations or journals. Use markup for lists."
journaller_instruction = "Help the user with their journal. The image may contain landscapes that contain nature, or animals, or plants. If there is none of these in the landscape, tell the user you are unable to help them with their journal and explain."