# LangGraph Agent

LangGraph agent with calculator and weather tools, based on AWS notebook tutorial.

## Files

- `my_agent_langgraph.py` - Agent implementation
- `deploy.py` - Deployment script
- `invoke_langgraph_agent.py` - Agent invocation script
- `requirements.txt` - Dependencies

## Usage

### Deploy
```bash
python deploy.py
```

### Invoke
```bash
python invoke_langgraph_agent.py <AGENT_ARN> "<PROMPT>"
```

### Examples
```bash
python invoke_langgraph_agent.py "YOUR-ARN" "What is 2+2?"
python invoke_langgraph_agent.py "YOUR-ARN" "What's the weather?"
```

## Tools

- **Calculator**: Safe mathematical calculations
- **Weather**: Weather information (demo)
