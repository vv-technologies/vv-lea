// LEA Voice — Voce input/output prin Web Speech API (browser built-in, zero dependențe)
// VV Hybrid Universe · Cosmin Toma

const LeaVoice = (function () {
  let _recognition = null;
  let _synthesis = typeof window !== 'undefined' ? window.speechSynthesis : null;
  let _listening = false;
  let _onResult = null;
  let _onError = null;

  function isSupported() {
    return typeof window !== 'undefined' &&
      ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
  }

  function isSpeechSupported() {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  // Porneste microfon
  function startMic(onResult, onError, lang = 'ro-RO') {
    if (!isSupported()) {
      if (onError) onError('Speech recognition not supported in this browser');
      return;
    }
    if (_listening) stopMic();

    _onResult = onResult;
    _onError = onError;

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    _recognition = new SR();
    _recognition.lang = lang;
    _recognition.continuous = false;
    _recognition.interimResults = false;
    _recognition.maxAlternatives = 1;

    _recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      _listening = false;
      if (_onResult) _onResult(transcript);
    };

    _recognition.onerror = (e) => {
      _listening = false;
      if (_onError) _onError(e.error);
    };

    _recognition.onend = () => { _listening = false; };

    _recognition.start();
    _listening = true;
  }

  // Opreste microfon
  function stopMic() {
    if (_recognition) {
      try { _recognition.stop(); } catch {}
    }
    _listening = false;
  }

  // Sintetizeaza text în voce
  function speak(text, lang = 'ro-RO', rate = 0.95, pitch = 1.0) {
    if (!isSpeechSupported()) return;
    _synthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = lang;
    utt.rate = rate;
    utt.pitch = pitch;

    // Preferinta pentru voce feminina
    const voices = _synthesis.getVoices();
    const preferred = voices.find(v => v.lang.startsWith('ro') && v.name.toLowerCase().includes('female'))
      || voices.find(v => v.lang.startsWith('ro'))
      || null;
    if (preferred) utt.voice = preferred;

    _synthesis.speak(utt);
  }

  // Opreste vocea
  function stopSpeak() {
    if (_synthesis) _synthesis.cancel();
  }

  // Toggle mic (util pentru buton)
  function toggleMic(onResult, onError) {
    if (_listening) { stopMic(); return false; }
    startMic(onResult, onError);
    return true;
  }

  return {
    startMic, stopMic, speak, stopSpeak, toggleMic,
    isListening: () => _listening,
    isSupported,
    isSpeechSupported
  };
})();

if (typeof module !== 'undefined') module.exports = LeaVoice;
