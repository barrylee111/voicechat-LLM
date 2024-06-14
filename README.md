## Overview
### Demo Link:
TBD

### VoiceChat
- Enables user to have a conversation with an LLM (Voice in, Voice out)
  - Voice input is working, Voice output is currently being constructed
- Enables user to select a `narrator` that will act according to the description. (The TTS models that will be invoked are part of the next build cycle: AI)
  - Pirate
  - Scotsman
  - More

### TextChat
  - Enables user to interact with an LLM via prompt
  - Auto-Complete (part of frontend build cycle) 

## Technologies Applied
### LLM
- ChatGPT

### Languages
- React (Coming in next build cycle)
- Python / FastAPI
- CSS: Tailwind

### Containerization
- Docker (Coming in next build cycle)

### Streaming flow of audio input
- Websockets

### Databases
- PostGreSQL (User/Auth)
- VectorDB (Domain specific knowlegdge - RAG architecture)

## Future Planning
### Clustering
- EKS / Kubernetes / Terraform

### LLM
Swap out ChatGPT for an SLM like Llama3 that is running on our own server.

### Mobile
- iOS
- Android