import axios from 'axios';

const baseURL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL,
});

export const generateLLMResponse = async (prompt, narrator, documents) => {
  let request = {
    prompt,
    documents
  }

  if (narrator && narrator !== 'none') {
    request = {
      ...request,
      narrator
    }
  }

  try {
    const response = await api.post('/chat/generate', request);
    return response.data;
  } catch (error) {
    throw new Error('Failed to generate prompt: ' + error.message);
  }
};
