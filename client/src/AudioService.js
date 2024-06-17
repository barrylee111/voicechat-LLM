import { Howl } from 'howler';

export const playAudio = (audioBytes) => {
  const blob = new Blob([audioBytes], { type: 'audio/wav' });
  const url = URL.createObjectURL(blob);

  const sound = new Howl({
    src: [url],
    format: ['wav'],
  });

  sound.play();
};
