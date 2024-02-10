from langchain.callbacks.base import BaseCallbackHandler

class MyStreamingCallback(BaseCallbackHandler):
    def __init__(self, g):
        self.content = ""
        self.final_answer = False
        self.g = g

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.content += token
        self.g.send(token)
        if "." in token:
            self.content += '\n'
            self.g.send('\n')
        if "final_answer" in self.content:
            self.final_answer = True 
            self.content = ""

    def on_llm_end(self, response, **kwargs) -> None:
        self.g.close()

class MyAgentCallback(BaseCallbackHandler):
    def __init__(self, g):
        self.content = ""
        self.final_answer = False
        self.g = g

    def on_agent_action(self, action):
        self.g.send(f"on_agent_action {action}")

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.content += token
        # self.g.send(token)
        # if "." in token:
        #     self.g.send('\n')
        if "Final Answer" in self.content:
            self.final_answer = True 
            self.g.send(token)
            # self.content = ""

    def on_llm_end(self, response, **kwargs) -> None:
        self.g.close()