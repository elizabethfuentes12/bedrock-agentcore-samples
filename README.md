# Starting with Amazon Bedrock AgentCore

<div align="center">
  
  [![License](https://img.shields.io/badge/License-MIT--0-blue.svg?style=for-the-badge)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.8+-green.svg?style=for-the-badge&logo=python)](https://python.org)
  [![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/bedrock/)
  
  
  <br>
  <p><em>Bring AI agents into production in minutes</em>
  </p>
   <p>⭐ Star this repository</p>
  
</div>

This repository contains hands-on labs demonstrating the capabilities of [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), a suite of services that enables you to deploy and operate highly effective AI agents securely at scale.

## What is Amazon Bedrock AgentCore?

Amazon Bedrock AgentCore enables developers to accelerate AI agents into production with enterprise-grade scale, reliability, and security. AgentCore provides composable services that work with popular open-source frameworks and any model, eliminating the choice between open-source flexibility and enterprise requirements.

### AgentCore Services Overview

![agentcore_overview](images/agentcore_overview.png)

| Service | Purpose | Key Features |
|---------|---------|--------------|
| **AgentCore Runtime** | Serverless execution | Auto-scaling, session management, container orchestration |
| **AgentCore Identity** | Credential management | API keys, OAuth tokens, secure vault |
| **AgentCore Memory** | State persistence | Short-term memory, long-term storage |
| **AgentCore Gateway** | API management | Tool discovery, service integration |
| **AgentCore Code Interpreter** | Code execution | Secure sandbox, data analysis |
| **AgentCore Browser** | Web interaction | Cloud browser, auto-scaling |
| **AgentCore Observability** | Monitoring | Tracing, dashboards, debugging |

## Overview

| 📓 Services | 🎯 Focus & Key Learning | ⏱️ Time | 📊 Level |
|-------------|------------------------|----------|----------|
| **01 - [Amazon Bedrock AgentCore Runtime](./01-agentcore-runtime/)** | Serverless AI agent deployment with auto-scaling, session management, and built-in security | 10 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | 
| **02 - [Amazon Bedrock AgentCore Memory](./02-agentcore-memory/)** | Context-aware memory for conversation context and cross-session knowledge retention | 10 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | 
| **03 - [Amazon Bedrock AgentCore Gateway](./03-agentcore-gateway/)** | Tool integration and discovery, converting existing services into agent-compatible tools | 10 min | ![Intermediate](https://img.shields.io/badge/-Intermediate-yellow) | 

---

## Detailed Lab Descriptions

| 📓 Services | 🎯 Focus & Key Learning | 🖼️ Diagram |
|-------------|------------------------|-------------|
| **Amazon Bedrock AgentCore Runtime** | **Focus**: [Serverless AI Agent Deployment](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)<br><br>Deploy production-ready AI agents with just 2 commands using AgentCore Runtime. This lab demonstrates:<br>• Serverless agent deployment with auto-scaling<br>• Session management and isolation<br>• Built-in security and authentication<br>• Integration with Strands Agents framework<br><br>**Key Learning**: Transform prototype agents into production-ready services in minutes, not weeks. | ![image](images/lab_01_runtime.png) |
| **Amazon Bedrock AgentCore Memory** | **Focus**: [Intelligent Memory Capabilities](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)<br><br>Add context-aware memory to AI agents using AgentCore Memory. This lab covers:<br>• Short-term memory for conversation context<br>• Long-term memory for user preferences<br>• Cross-session knowledge retention<br>• Personalized agent experiences<br><br>**Key Learning**: Build agents that remember and learn from interactions to provide more intelligent responses. | ![memory](images/high_level_memory.png) |
| **Amazon Bedrock AgentCore Gateway** | **Focus**: [Tool Integration and Discovery](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)<br><br>>Based on [Integrate Amazon Bedrock AgentCore Gateway with Amazon Bedrock AgentCore Runtime](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/02-AgentCore-gateway/04-integration/01-runtime-gateway)<br><br>Transform existing services into agent-compatible tools using AgentCore Gateway. This lab demonstrates:<br>• Converting Lambda functions to MCP tools<br>• Multi-target gateway configuration<br>• AWS IAM authentication for secure access<br>• Tool discovery and pagination<br><br>**Key Learning**: Integrate existing enterprise resources as agent tools without custom development. | ![image](images/lab_03_architecture.png) |

Transform existing services into agent-compatible tools using AgentCore Gateway. This lab demonstrates:
- Converting Lambda functions to MCP tools
- Multi-target gateway configuration
- AWS IAM authentication for secure access
- Tool discovery and pagination

## Getting Started

Each lab includes:
- **Prerequisites**: Required setup and dependencies
- **Step-by-step deployment**: Automated infrastructure setup
- **Sample interactions**: Real-world usage examples
- **Code explanations**: Detailed implementation walkthrough
- **Cleanup instructions**: Resource removal

### Optional: Generic Deployment Script

For convenience, a generic deployment script is available at the root level:

```bash
# Deploy with auto-created execution role
python deploy.py lab01/langgraph

# Deploy with existing execution role
python deploy.py lab01/langgraph YOUR-AGENT-ROLE
```


## Key Benefits of AgentCore

### Traditional vs AgentCore Deployment

| Traditional Deployment | AgentCore Deployment |
|----------------------|---------------------|
| ❌ 3+ weeks setup | ✅ 15 minutes |
| ❌ Docker + Kubernetes | ✅ Serverless |
| ❌ Manual scaling | ✅ Auto-scaling |
| ❌ Complex security | ✅ Built-in security |
| ❌ DevOps expertise required | ✅ 2 commands |

## Prerequisites

Before starting any lab, ensure you have:
- AWS Account with appropriate permissions
- Python 3.10+ installed
- AWS CLI configured
- Basic understanding of AI agents and AWS services

## Resources

### Documentation
- [What is Amazon Bedrock AgentCore?](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [AgentCore Runtime How It Works](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [AgentCore Memory Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Programmatic Agent Invocation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html#invoke-programmatically)

### Code Examples
- [AWS Labs AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)

## Lab Structure

```
test-ga/
├── lab01/          # AgentCore Runtime - Basic deployment
├── lab02/          # AgentCore Memory - Context-aware agents  
├── lab03/          # AgentCore Gateway - Tool integration
└── README.md       # This overview
```

Each lab is self-contained with its own README, code samples, and infrastructure templates.

---

**Ready to deploy production AI agents?** Start with [01-agentcore-runtime](./01-agentcore-runtime/) to learn the fundamentals of AgentCore Runtime.

---

## 🇻🇪🇨🇱 ¡Gracias!

[Dev.to](https://dev.to/elizabethfuentes12) [Linkedin](https://www.linkedin.com/in/lizfue/) [GitHub](https://github.com/elizabethfuentes12/) [Twitter](https://twitter.com/elizabethfue12) [Instagram](https://www.instagram.com/elifue.tech) [Youtube](https://www.youtube.com/channel/UCr0Gnc-t30m4xyrvsQpNp2Q)
[Linktr](https://linktr.ee/elizabethfuentesleone)
---

## 📄 License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.
