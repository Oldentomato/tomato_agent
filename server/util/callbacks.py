from langchain.callbacks.base import BaseCallbackHandler

class MyStreamingCallback(BaseCallbackHandler):
    def __init__(self, g):
        self.content = ""
        self.final_answer = False
        self.g = g


    def on_agent_action(self, action, run_id, parent_run_id):
        self.g.send(f"on_agent_action {action}")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.content += token
        self.g.send(token)



class MyAgentCallback(BaseCallbackHandler):
    def __init__(self, g):
        self.content = ""
        self.final_answer = False
        self.g = g

    def on_agent_action(self, action, **kwargs):
        self.g.send(f"**{action.tool_input}이라는 입력으로 {action.tool}도구를 사용합니다.**\n")

    def on_chain_end(self,outputs,**kwargs):
        self.g.close()
