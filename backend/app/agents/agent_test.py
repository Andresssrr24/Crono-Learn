from pomodoro_agent import agent_executor

msg = "Let's start a 10 minute timer"
token = 'asljkhdsjkfhadsklj'
rsp = agent_executor.invoke({"input": msg, "token": token})

print(rsp)