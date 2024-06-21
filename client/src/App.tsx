import React, { useState } from 'react';
import { generateLLMResponse } from './TextService';
import { Styles } from './Styles';
import { AppText as text } from './Text';
import { MicrophoneIcon } from '@heroicons/react/16/solid';

const App: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [narrator, setNarrator] = useState('');
  const [responseText, setResponseText] = useState('');

  const handleGenerateLLMResponse = async (): Promise<void> => {
    try {
      const response = await generateLLMResponse(prompt, narrator);
      setResponseText(response.response);
    } catch (error) {
      console.error('Error generating LLM response:', error);
      setResponseText('Failed to generate LLM response');
    }
  };

  return (
    <div className={Styles.container}>
      <h1 className={Styles.h1}>{text.main_header}</h1>
      <div className={Styles.narrator}>
        <h2 className={Styles.h2}>{text.select_narrator}</h2>
        <select 
          id="narrator" 
          value={narrator} 
          onChange={(e) => setNarrator(e.target.value)}
        >
          {Object.entries(text.narrator_options).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>
      <div>
        <h2 className={Styles.h2}>{text.response_header}</h2>
        <textarea
          id="conversation"
          value={responseText}
          onChange={(e) => setResponseText(e.target.value)}
          className={Styles.conversation}
          readOnly
          aria-live="polite"
        />
      </div>
      <div className={Styles.prompt}>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className={Styles.prompt_window}
          required
        />
      </div>
      <div>
        <button
          className={Styles.button}
          onClick={handleGenerateLLMResponse}
        >
          {text.button}
        </button>
        <MicrophoneIcon className={Styles.microphone} />
      </div>
    </div>
  );
}

export default App;
