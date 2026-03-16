/* ================================================================
   WhisperMind Frontend — vanilla JS
   API base: /api/v1/speech
   ================================================================ */

const API = '/api/v1/speech';

//  State─
const state = {
  recording:    false,
  mediaRecorder: null,
  audioChunks:  [],
  recordStart:  null,
  timer:        null,
  transcript:   '',
  recordId:     null,
  selectedMode: 'smart_summary',
};

//  DOM refs
const $ = id => document.getElementById(id);

const btnSpeak          = $('btnSpeak');
const micOrbit          = $('micOrbit');
const statusBadge       = $('statusBadge');
const statusText        = $('statusText');
const waveform          = $('waveform');
const countdownWrap     = $('countdownWrap');
const countdownFill     = $('countdownFill');
const countdownLabel    = $('countdownLabel');
const transcriptSection = $('transcriptSection');
const transcriptText    = $('transcriptText');
const transcriptPills   = $('transcriptPills');
const geminiText        = $('geminiText');
const geminiResult      = $('geminiResult');
const geminiPills       = $('geminiPills');
const historyList       = $('historyList');
const histCount         = $('histCount');

//  Helpers─
function toast(msg, type = 'info', duration = 3500) {
  const icons = { success: 'check-circle', error: 'exclamation-triangle', info: 'info-circle' };
  const el = document.createElement('div');
  el.className = `sf-toast ${type}`;
  el.innerHTML = `<i class="bi bi-${icons[type] || 'info-circle'}"></i><span>${msg}</span>`;
  $('toastStack').appendChild(el);
  setTimeout(() => el.remove(), duration);
}

function setStatus(mode, text) {
  statusBadge.className = `status-badge ${mode} mt-3`;
  statusText.textContent = text;
  waveform.className = mode === 'rec' ? 'waveform active' : 'waveform';
}

function pill(label, type = '') {
  return `<span class="pill ${type}">${label}</span>`;
}

function wordCount(text) {
  return text.trim() ? text.trim().split(/\s+/).length : 0;
}

function fmtDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Copy-to-clipboard helper
function setupCopyBtn(btnId, getTextFn) {
  const btn = $(btnId);
  if (!btn) return;
  btn.addEventListener('click', () => {
    navigator.clipboard.writeText(getTextFn()).then(() => {
      btn.classList.add('copied');
      btn.innerHTML = '<i class="bi bi-clipboard-check me-1"></i>Copied!';
      setTimeout(() => {
        btn.classList.remove('copied');
        btn.innerHTML = '<i class="bi bi-clipboard me-1"></i>Copy';
      }, 2000);
    });
  });
}

//  Mode chips
document.querySelectorAll('.mode-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.mode-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.selectedMode = chip.dataset.mode;
  });
});

//  Recording logic ─
btnSpeak.addEventListener('click', () => {
  if (state.recording) return;
  startRecording();
});

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.audioChunks = [];
    state.recording = true;
    state.recordStart = Date.now();

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm';

    state.mediaRecorder = new MediaRecorder(stream, { mimeType });
    state.mediaRecorder.ondataavailable = e => { if (e.data.size) state.audioChunks.push(e.data); };
    state.mediaRecorder.onstop = handleRecordingStop;
    state.mediaRecorder.start(250);  // collect in 250 ms chunks

    // UI
    btnSpeak.disabled = true;
    micOrbit.classList.add('is-listening');
    setStatus('rec', 'Recording…');
    countdownWrap.classList.add('visible');

    const maxDur = parseInt($('cfgDuration').value, 10);
    let elapsed = 0;
    state.timer = setInterval(() => {
      elapsed++;
      const pct = Math.min((elapsed / maxDur) * 100, 100);
      countdownFill.style.width = pct + '%';
      countdownLabel.textContent = `Listening · ${elapsed}s`;
      if (elapsed >= maxDur) stopRecording();
    }, 1000);

  } catch (err) {
    toast('Microphone access denied — ' + err.message, 'error');
    console.error(err);
  }
}

function stopRecording() {
  if (!state.recording) return;
  clearInterval(state.timer);
  state.mediaRecorder.stop();
  state.mediaRecorder.stream.getTracks().forEach(t => t.stop());
  state.recording = false;
}

// Stop button (double-click mic to stop early)
micOrbit.addEventListener('dblclick', stopRecording);
$('micCore').title = 'Double-click to stop early';

async function handleRecordingStop() {
  // Reset UI
  micOrbit.classList.remove('is-listening');
  btnSpeak.disabled = false;
  countdownWrap.classList.remove('visible');
  countdownFill.style.width = '0%';

  setStatus('proc', 'Transcribing…');
  transcriptSection.style.display = 'block';
  $('transcriptOverlay').classList.add('visible');
  $('overlayMsg').textContent = 'Transcribing…';

  const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
  const duration = ((Date.now() - state.recordStart) / 1000).toFixed(1);

  const fd = new FormData();
  fd.append('file', blob, 'recording.webm');
  fd.append('whisper_model', $('cfgModel').value);
  const lang = $('cfgLang').value;
  if (lang) fd.append('language', lang);

  try {
    const res = await fetch(`${API}/transcribe`, { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();

    state.transcript = data.transcript;
    state.recordId   = data.record_id;

    transcriptText.textContent = data.transcript;

    // Pills
    const wc  = data.word_count || wordCount(data.transcript);
    const dur = data.duration_sec ? `${data.duration_sec}s` : `~${duration}s`;
    transcriptPills.innerHTML =
      pill(`⏱ ${dur}`, 'pill-amber') +
      pill(`📝 ${wc} words`, 'pill-amber') +
      pill(`Whisper ${data.whisper_model}`) +
      pill('FFmpeg');

    // Stats (fetch analysis)
    fetchAnalysis(data.record_id);

    setStatus('success', 'Transcription complete');
    toast('Transcription ready!', 'success');

    // Refresh history
    loadHistory();

  } catch (err) {
    transcriptText.textContent = `⚠️ Error: ${err.message}`;
    setStatus('error', 'Transcription failed');
    toast('Transcription failed — ' + err.message, 'error');
    console.error(err);
  } finally {
    $('transcriptOverlay').classList.remove('visible');
  }
}

//  Analysis / stats 
async function fetchAnalysis(recordId) {
  try {
    const res = await fetch(`${API}/analyse/${recordId}`);
    if (!res.ok) return;
    const data = await res.json();
    $('statWords').textContent     = data.word_count;
    $('statSentences').textContent = data.sentence_count;
    $('statRead').textContent      = data.reading_time_sec + 's';
    $('statsRow').style.display    = '';
  } catch {}
}

//  Gemini enhance 
$('btnRunGemini').addEventListener('click', async () => {
  if (!state.transcript) { toast('Record something first!', 'error'); return; }

  const btn = $('btnRunGemini');
  const spinner = $('geminiSpinner');
  const label = $('btnRunLabel');

  btn.disabled = true;
  spinner.classList.remove('d-none');
  label.textContent = 'Running…';
  $('geminiOverlay').classList.add('visible');

  try {
    const res = await fetch(`${API}/enhance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: state.transcript,
        mode: state.selectedMode,
        record_id: state.recordId,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }

    const data = await res.json();

    geminiText.textContent = data.gemini_output;
    geminiResult.style.display = 'block';
    $('btnCopyGemini').style.display = '';

    const modeLabel = document.querySelector(`.mode-chip[data-mode="${state.selectedMode}"]`)?.textContent || state.selectedMode;
    geminiPills.innerHTML =
      pill(`🤖 Gemini Flash`, 'pill-cyan') +
      pill(modeLabel, 'pill-cyan');

    toast('Gemini response ready!', 'info');
    loadHistory();

  } catch (err) {
    geminiText.textContent = `⚠️ Error: ${err.message}`;
    geminiResult.style.display = 'block';
    toast('Gemini failed — ' + err.message, 'error');
    console.error(err);
  } finally {
    btn.disabled = false;
    spinner.classList.add('d-none');
    label.textContent = 'Run';
    $('geminiOverlay').classList.remove('visible');
  }
});

//  Clear
$('btnClear').addEventListener('click', () => {
  state.transcript = '';
  state.recordId   = null;
  transcriptSection.style.display = 'none';
  geminiResult.style.display = 'none';
  $('btnCopyGemini').style.display = 'none';
  $('statsRow').style.display = 'none';
  setStatus('idle', 'Ready to record');
});

//  History
async function loadHistory() {
  try {
    const res = await fetch(`${API}/history?limit=20`);
    if (!res.ok) return;
    const data = await res.json();

    histCount.textContent = `${data.total} record${data.total !== 1 ? 's' : ''}`;

    if (!data.items.length) {
      historyList.innerHTML = '<div class="empty-state">No recordings yet — press Speak to start</div>';
      return;
    }

    historyList.innerHTML = data.items.map(item => `
      <div class="history-entry" id="hist-${item.id}">
        <div class="hist-meta">
          #${item.id}
          &nbsp;·&nbsp; ${fmtDate(item.created_at)}
          ${item.duration_sec ? `&nbsp;·&nbsp; ${item.duration_sec}s` : ''}
          ${item.word_count   ? `&nbsp;·&nbsp; ${item.word_count} words` : ''}
          ${item.gemini_mode  ? `&nbsp;·&nbsp; ${item.gemini_mode.replace('_',' ')}` : ''}
          <button class="btn-del-hist" data-id="${item.id}" title="Delete">
            <i class="bi bi-trash"></i>
          </button>
        </div>
        <div class="hist-transcript">
          <strong>Transcript:</strong> ${escapeHtml(item.transcript.slice(0, 200))}${item.transcript.length > 200 ? '…' : ''}
        </div>
        ${item.gemini_output ? `
        <div class="hist-gemini mt-1">
          <strong>Gemini:</strong> ${escapeHtml(item.gemini_output.slice(0, 250))}${item.gemini_output.length > 250 ? '…' : ''}
        </div>` : ''}
      </div>
    `).join('');

    // Delete buttons
    historyList.querySelectorAll('.btn-del-hist').forEach(btn => {
      btn.addEventListener('click', () => deleteRecord(parseInt(btn.dataset.id)));
    });

  } catch (err) {
    console.error('History load error:', err);
  }
}

async function deleteRecord(id) {
  try {
    const res = await fetch(`${API}/history/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
    document.getElementById(`hist-${id}`)?.remove();
    toast('Record deleted', 'success');
    loadHistory();
  } catch (err) {
    toast('Delete failed — ' + err.message, 'error');
  }
}

$('btnRefreshHistory').addEventListener('click', loadHistory);

//  Copy buttons
setupCopyBtn('btnCopyTranscript', () => state.transcript);
setupCopyBtn('btnCopyGemini', () => geminiText.textContent);

//  XSS guard─
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

//  Health check on load 
async function checkHealth() {
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    if (!data.gemini_configured) toast('Gemini API key not configured — add SPEECH= to .env', 'error', 6000);
    if (!data.whisper_available) toast('Whisper not installed — pip install openai-whisper', 'error', 6000);
  } catch {
    toast('Cannot reach server', 'error');
  }
}

//  Init
checkHealth();
loadHistory();