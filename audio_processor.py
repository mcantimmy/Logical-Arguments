import whisper
import torch
import librosa
import soundfile as sf
import tempfile
import os
from pydub import AudioSegment
from typing import Dict, List, Optional, Tuple
import config

class AudioProcessor:
    """Handles audio file processing and transcription."""
    
    def __init__(self, model_name: str = config.WHISPER_MODEL):
        """Initialize the audio processor with a Whisper model."""
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            self.model = whisper.load_model(self.model_name)
            print(f"Loaded Whisper model: {self.model_name}")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the audio file format is supported."""
        _, ext = os.path.splitext(file_path.lower())
        return ext in config.SUPPORTED_AUDIO_FORMATS
    
    def convert_audio_format(self, input_path: str, output_path: str = None) -> str:
        """Convert audio to a format compatible with Whisper."""
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "converted_audio.wav")
        
        try:
            # Check if file is already WAV format
            _, ext = os.path.splitext(input_path.lower())
            if ext == '.wav':
                # For WAV files, try to use directly without conversion
                try:
                    # Test if the file can be loaded with librosa (which doesn't require ffmpeg)
                    import librosa
                    audio_data, sample_rate = librosa.load(input_path, sr=16000, mono=True)
                    # If successful, save as WAV using soundfile
                    import soundfile as sf
                    sf.write(output_path, audio_data, 16000)
                    return output_path
                except Exception as librosa_error:
                    print(f"Librosa conversion failed: {librosa_error}")
                    # Fall back to pydub if librosa fails
                    pass
            
            # Load audio with pydub for format conversion (requires ffmpeg)
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and standard sample rate
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            return output_path
        except Exception as e:
            print(f"Error converting audio format: {e}")
            # If conversion fails, try to use the original file directly
            if ext == '.wav':
                print("Attempting to use original WAV file directly...")
                return input_path
            raise
    
    def transcribe_audio(self, file_path: str, detect_speakers: bool = True) -> Dict:
        """
        Transcribe audio file and attempt to detect speakers.
        
        Args:
            file_path: Path to the audio file
            detect_speakers: Whether to attempt speaker detection
            
        Returns:
            Dictionary containing transcription results with speaker information
        """
        try:
            # Convert to compatible format if necessary
            if not self.is_supported_format(file_path):
                raise ValueError(f"Unsupported audio format. Supported formats: {config.SUPPORTED_AUDIO_FORMATS}")
            
            converted_path = self.convert_audio_format(file_path)
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                converted_path,
                word_timestamps=True,
                verbose=True
            )
            
            # Process segments for speaker detection
            processed_segments = self._process_segments(result["segments"], detect_speakers)
            
            # Clean up temporary file
            if converted_path != file_path:
                os.unlink(converted_path)
            
            return {
                "text": result["text"],
                "language": result["language"],
                "segments": processed_segments,
                "speakers": self._extract_speakers(processed_segments)
            }
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            raise
    
    def _process_segments(self, segments: List[Dict], detect_speakers: bool = True) -> List[Dict]:
        """Process transcript segments and attempt basic speaker detection."""
        processed_segments = []
        
        for i, segment in enumerate(segments):
            processed_segment = {
                "id": segment["id"],
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "speaker": self._detect_speaker(segment, i, segments) if detect_speakers else f"Speaker_{i % 2 + 1}"
            }
            processed_segments.append(processed_segment)
        
        return processed_segments
    
    def _detect_speaker(self, segment: Dict, index: int, all_segments: List[Dict]) -> str:
        """
        Basic speaker detection based on pauses and audio characteristics.
        This is a simple heuristic - for better results, use a dedicated speaker diarization model.
        """
        # Simple heuristic: assume speaker changes after longer pauses
        if index == 0:
            return "Speaker_1"
        
        previous_segment = all_segments[index - 1]
        pause_duration = segment["start"] - previous_segment["end"]
        
        # If there's a pause longer than 2 seconds, assume speaker change
        if pause_duration > 2.0:
            # Alternate between speakers based on segment index
            return f"Speaker_{(index // 2) % 2 + 1}"
        else:
            # Continue with previous speaker
            previous_speaker = f"Speaker_{((index - 1) // 2) % 2 + 1}"
            return previous_speaker
    
    def _extract_speakers(self, segments: List[Dict]) -> List[str]:
        """Extract unique speakers from segments."""
        speakers = list(set([segment["speaker"] for segment in segments]))
        return sorted(speakers)
    
    def get_audio_duration(self, file_path: str) -> float:
        """Get the duration of an audio file in seconds."""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0.0
    
    def split_audio_by_speaker(self, file_path: str, segments: List[Dict]) -> Dict[str, List[Tuple[float, float, str]]]:
        """
        Split audio segments by speaker.
        
        Returns:
            Dictionary mapping speaker names to list of (start_time, end_time, text) tuples
        """
        speaker_segments = {}
        
        for segment in segments:
            speaker = segment["speaker"]
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            
            speaker_segments[speaker].append((
                segment["start"],
                segment["end"],
                segment["text"]
            ))
        
        return speaker_segments 