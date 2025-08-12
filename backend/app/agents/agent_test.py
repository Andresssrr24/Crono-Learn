from groq_agent import agent_executor, create_pomodoro_tool

msg = 'pls start a 2 min pomodoro with 1 min of rest and task called Coding'
token = "lkasjfglkadsjgkldsaj"
params = {"input": msg, "token": token}
agent_executor.invoke({"input": msg, "token": token})

print(create_pomodoro_tool.args_schema.model_json_schema())