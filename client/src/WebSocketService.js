import useWebSocket from 'react-use-websocket';

// Your existing WebSocketService code here
const useGenerateResponse = (onMessage) => {
  const { sendMessage } = useWebSocket('ws://localhost:8000/ws/generate', {
    onMessage,
    shouldReconnect: () => true,
  });

  return { sendMessage };
};

export { useGenerateResponse };
