/**
 * Audio Utilities for Gemini Live Voice Controller
 * Includes resampling to 16kHz and proper PCM16 conversion
 */

/**
 * Resample audio buffer to 16kHz using OfflineAudioContext
 * @param audioBuffer - Source audio buffer
 * @returns Float32Array resampled to 16kHz
 */
export async function resampleTo16k(audioBuffer: AudioBuffer): Promise<Float32Array> {
  const targetRate = 16000;
  
  // If already at target rate, return directly
  if (audioBuffer.sampleRate === targetRate) {
    return audioBuffer.getChannelData(0);
  }

  // Use OfflineAudioContext to resample
  const offlineCtx = new OfflineAudioContext(
    1, // mono
    Math.ceil(audioBuffer.duration * targetRate),
    targetRate
  );
  
  const src = offlineCtx.createBufferSource();
  src.buffer = audioBuffer;
  src.connect(offlineCtx.destination);
  src.start(0);
  
  const rendered = await offlineCtx.startRendering();
  return rendered.getChannelData(0);
}

/**
 * Convert Float32Array to 16-bit PCM base64
 * @param float32 - Float32Array audio data
 * @returns Object with base64 data and mimeType
 */
export function floatTo16BitPCMBase64(float32: Float32Array): { data: string; mimeType: string } {
  const l = float32.length;
  const buffer = new ArrayBuffer(l * 2);
  const view = new DataView(buffer);
  let offset = 0;
  
  for (let i = 0; i < l; i++, offset += 2) {
    // Clamp to [-1, 1] and convert to 16-bit integer
    let s = Math.max(-1, Math.min(1, float32[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true); // little-endian
  }
  
  // Convert to base64 in chunks to avoid stack overflow
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000; // 32KB chunks
  
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, Math.min(i + chunkSize, bytes.length));
    binary += String.fromCharCode(...Array.from(chunk));
  }
  
  const base64 = btoa(binary);
  return { data: base64, mimeType: 'audio/pcm;rate=16000' };
}

/**
 * Legacy method - creates PCM blob from Float32Array without resampling
 * @deprecated Use resampleTo16k + floatTo16BitPCMBase64 instead
 */
export function createPcmBlob(float32: Float32Array): { data: string; mimeType: string } {
  console.warn('createPcmBlob: Consider using resampleTo16k + floatTo16BitPCMBase64 for proper resampling');
  return floatTo16BitPCMBase64(float32);
}

/**
 * Decode base64 audio data to ArrayBuffer
 * @param base64 - Base64 encoded audio data
 * @returns ArrayBuffer
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  return bytes.buffer;
}

/**
 * Decode base64 audio to Uint8Array
 * @param base64 - Base64 encoded audio
 * @returns Uint8Array
 */
export function base64ToUint8Array(base64: string): Uint8Array {
  return new Uint8Array(base64ToArrayBuffer(base64));
}

/**
 * Decode PCM16 audio data for playback
 * @param audioContext - Web Audio API context
 * @param base64Data - Base64 encoded PCM16 data
 * @param sampleRate - Sample rate of the audio (default 24000 for Gemini output)
 * @returns Promise<AudioBuffer>
 */
export async function decodeAudioData(
  audioContext: AudioContext,
  base64Data: string,
  sampleRate: number = 24000
): Promise<AudioBuffer> {
  const arrayBuffer = base64ToArrayBuffer(base64Data);
  const int16Array = new Int16Array(arrayBuffer);
  
  // Convert Int16 PCM to Float32
  const float32Array = new Float32Array(int16Array.length);
  for (let i = 0; i < int16Array.length; i++) {
    float32Array[i] = int16Array[i] / (int16Array[i] < 0 ? 0x8000 : 0x7FFF);
  }
  
  // Create audio buffer
  const audioBuffer = audioContext.createBuffer(1, float32Array.length, sampleRate);
  audioBuffer.copyToChannel(float32Array, 0);
  
  return audioBuffer;
}

/**
 * Create a silent gain node to prevent audio feedback
 * @param audioContext - Web Audio API context
 * @returns GainNode with gain set to 0
 */
export function createSilentGainNode(audioContext: AudioContext): GainNode {
  const gainNode = audioContext.createGain();
  gainNode.gain.value = 0;
  return gainNode;
}

/**
 * Resume AudioContext (required after user interaction on some browsers)
 * @param audioContext - AudioContext to resume
 */
export async function resumeAudioContext(audioContext: AudioContext): Promise<void> {
  if (audioContext.state === 'suspended') {
    await audioContext.resume();
  }
}

/**
 * Check if browser supports AudioWorklet (better alternative to ScriptProcessor)
 * @returns boolean
 */
export function supportsAudioWorklet(): boolean {
  return typeof AudioWorklet !== 'undefined';
}
