import React, { useState } from 'react';
import { generateLLMResponse } from './TextService';
import { ButtonStyle, ContainerStyle, TextAreaStyle } from './Styles';
import { AppText as text } from './Text';

const App = () => {
  const [prompt, setPrompt] = useState('');
  const [narrator, setNarrator] = useState('');
  const [responseText, setResponseText] = useState('');

  const handleGenerateLLMResponse = async () => {
    try {
      const response = await generateLLMResponse(prompt, narrator);
      setResponseText(response.response);
    } catch (error) {
      console.error('Error generating LLM response:', error);
      setResponseText('Failed to generate LLM response');
    }
  };

  return (
    <div style={ContainerStyle}>
      <h1>{text.main_header}</h1>
      <div style={{ marginBottom: '25px' }}>
        <h2>{text.select_narrator}</h2>
        <select 
          id="narrator" 
          value={narrator} 
          onChange={(e) => setNarrator(e.target.value)}
        >
          {Object.entries(text.narrator_options).map(([k, v]) => (
            <option
              key={k}
              value={k}
            >{v}</option>
          ))}
        </select>
      </div>
      <div>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={TextAreaStyle}
          required
        />
      </div>
      <div>
        <button
          style={ButtonStyle}
          onClick={handleGenerateLLMResponse}
        >{text.button}</button>
      </div>
      <div>
        <h2>{text.response_header}</h2>
        <textarea
          id="response"
          value={responseText}
          style={TextAreaStyle}
          readOnly
        />
      </div>
    </div>
  );
}

export default App;
