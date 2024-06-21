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

### Backend Server
- FastAPI - Text-To-Text and Speech-To-Speech Flows (Next Build Cycle)
- Django - User creation, authentication, and authorization

### Languages
- React
- Typescript
- Python
- CSS: Tailwind

### Containerization
- Docker (Next build cycle)

### Streaming flow of audio input
- Websockets

### Databases
- PostGreSQL (User/Auth - Next Build Cycle)
- VectorDB (Domain specific knowlegdge - RAG architecture)

## Future Planning
### Conversations
- User will be able to select any of their previous conversations (limit of X)
- When selected the convo will populate into the history window above the TextPrompt

### Documents
- User will be able to upload a doc that will either:
  - passed in as a one-off for the text or voice-chat prompt
  - stored permanently as a doc that is referenced when they query the LLM

### User Account Creation and Auth
- A new service will be constructed in Django to enable noobs to:
  - Register an account
  - Log in
  - Delete the account
  - Auth for use of LLM

### Clustering
- EKS / Kubernetes / Terraform

### LLM To SLM
Swap out ChatGPT for an SLM like Llama3 that is running on our own server.

### Mobile Versions
- iOS
- Android