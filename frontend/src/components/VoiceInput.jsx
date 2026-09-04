import { useState } from "react";

function VoiceInput({ onTranscript, disabled = false }) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);

  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript =
        event.results[0][0].transcript;

      onTranscript(transcript);
    };

    recognition.onerror = () => {
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  };

  return (
    <div className="voice-area">
      <button
        type="button"
        className={`voice-button ${
          listening ? "listening" : ""
        }`}
        onClick={startListening}
        disabled={disabled || listening}
      >
        {listening
          ? "● Listening..."
          : "🎙 Speak Symptoms"}
      </button>

      {!supported && (
        <span className="voice-note">
          Voice input is unavailable. Please use manual entry.
        </span>
      )}
    </div>
  );
}

export default VoiceInput;