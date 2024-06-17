import React, { useState } from 'react';
import { generateLLMResponse } from './TextService';

const App = () => {
  const [prompt, setPrompt] = useState('');
  const [narrator, setNarrator] = useState('');
  const [documents, setDocuments] = useState('');
  const [responseText, setResponseText] = useState('');

  const handleGenerateLLMResponse = async () => {
    try {
      const response = await generateLLMResponse(prompt, narrator, documents);
      setResponseText(response.response);
    } catch (error) {
      console.error('Error generating LLM response:', error);
      setResponseText('Failed to generate LLM response');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'center' }} className="App">
      <h1>VoiceChat LLM</h1>
      <div style={{ marginBottom: '25px' }}>
        <h2>Select Narrator</h2>
        <select 
          id="narrator" 
          value={narrator} 
          onChange={(e) => setNarrator(e.target.value.toLowerCase())}
        >
          <option value="None">None</option>
          <option value="Pirate">Pirate</option>
          <option value="Scotsman">Scotsman</option>
        </select>
      </div>
      <div>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ height: '100px', resize: 'vertical', width: '25%' }}
          required
        />
      </div>
      <div>
        <button style={{ width: '25%' }} onClick={handleGenerateLLMResponse}>Generate Prompt</button>
      </div>
      <div>
        <h2>Generated Response:</h2>
        <p>{responseText}</p>
      </div>
    </div>
  );
}

export default App;
