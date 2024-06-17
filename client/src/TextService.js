import axios from 'axios';

const baseURL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL,
});

export const generateLLMResponse = async (prompt, narrator, documents) => {
  console.log(`prompt: ${prompt}, narrator: ${narrator}`)
  try {
    const response = await api.post('/chat/generate', {
      prompt,
      narrator,
      documents,
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to generate prompt: ' + error.message);
  }
};
