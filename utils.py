"""
Utility functions for the Debate Audio to Formal Logic Converter.

This module contains helper functions for file handling, validation,
and common operations used across the application.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import config

def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if a file is a supported audio format.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > config.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = config.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB (max: {max_mb:.1f}MB)"
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in config.SUPPORTED_AUDIO_FORMATS:
            return False, f"Unsupported format: {ext}. Supported: {', '.join(config.SUPPORTED_AUDIO_FORMATS)}"
        
        # Check MIME type if possible
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and not mime_type.startswith('audio'):
            return False, f"File does not appear to be audio: {mime_type}"
        
        return True, "File is valid"
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2:30", "1:05:30")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def ensure_output_directory() -> str:
    """
    Ensure the output directory exists and return its path.
    
    Returns:
        Path to the output directory
    """
    output_dir = Path(config.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)

def get_sample_audio_files() -> List[Dict[str, str]]:
    """
    Get information about available sample audio files.
    
    Returns:
        List of dictionaries with file information
    """
    sample_files = []
    sample_dir = Path(config.SAMPLE_AUDIO_DIR)
    
    if not sample_dir.exists():
        return sample_files
    
    for file_path in sample_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in config.SUPPORTED_AUDIO_FORMATS:
            try:
                file_size = file_path.stat().st_size
                sample_files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_size,
                    'size_formatted': format_file_size(file_size),
                    'extension': file_path.suffix.lower()
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    return sorted(sample_files, key=lambda x: x['name'])

def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove or replace problematic characters
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Ensure text ends with proper punctuation
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text.strip()

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_speaker_stats(transcription_data: Dict) -> Dict[str, Dict]:
    """
    Extract statistics about speakers from transcription data.
    
    Args:
        transcription_data: Transcription result dictionary
        
    Returns:
        Dictionary with speaker statistics
    """
    stats = {}
    segments = transcription_data.get("segments", [])
    
    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        
        if speaker not in stats:
            stats[speaker] = {
                "segment_count": 0,
                "total_duration": 0.0,
                "word_count": 0,
                "first_appearance": float('inf'),
                "last_appearance": 0.0
            }
        
        # Update statistics
        stats[speaker]["segment_count"] += 1
        duration = segment.get("end", 0) - segment.get("start", 0)
        stats[speaker]["total_duration"] += duration
        stats[speaker]["word_count"] += len(segment.get("text", "").split())
        stats[speaker]["first_appearance"] = min(stats[speaker]["first_appearance"], segment.get("start", 0))
        stats[speaker]["last_appearance"] = max(stats[speaker]["last_appearance"], segment.get("end", 0))
    
    # Format durations
    for speaker_stats in stats.values():
        speaker_stats["duration_formatted"] = format_duration(speaker_stats["total_duration"])
        if speaker_stats["first_appearance"] == float('inf'):
            speaker_stats["first_appearance"] = 0.0
    
    return stats

def generate_filename(base_name: str, extension: str = ".docx", timestamp: bool = True) -> str:
    """
    Generate a filename with optional timestamp.
    
    Args:
        base_name: Base name for the file
        extension: File extension (including dot)
        timestamp: Whether to include timestamp
        
    Returns:
        Generated filename
    """
    from datetime import datetime
    
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp_str}{extension}"
    else:
        return f"{base_name}{extension}"

def safe_filename(filename: str) -> str:
    """
    Make a filename safe for the filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove multiple underscores
    while '__' in safe_name:
        safe_name = safe_name.replace('__', '_')
    
    # Trim length if too long
    if len(safe_name) > 200:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:200-len(ext)] + ext
    
    return safe_name.strip('_')

def create_sample_debate_text() -> str:
    """
    Create sample debate text for testing purposes.
    
    Returns:
        Sample debate text that can be converted to audio
    """
    return """
Speaker 1: Thank you for joining today's debate on renewable energy policy. I believe that government subsidies for renewable energy are essential for addressing climate change. My argument is straightforward: first, climate change poses an existential threat to humanity. Second, renewable energy is the most viable solution to reduce carbon emissions. Third, without government intervention, the transition to renewable energy will be too slow. Therefore, substantial government subsidies are not just beneficial, but necessary.

Speaker 2: I respectfully disagree with my colleague's position. While I acknowledge the importance of addressing climate change, I believe that government subsidies for renewable energy are economically inefficient and ultimately counterproductive. Here's my reasoning: first, subsidies distort market mechanisms and prevent the most efficient energy solutions from emerging naturally. Second, they create dependencies and reduce innovation incentives. Third, the tax burden required to fund these subsidies harms economic growth. A better approach would be to remove barriers and let market forces drive the transition to cleaner energy.

Speaker 1: My opponent raises market concerns, but this argument ignores market failures. The energy market doesn't account for environmental externalities. Carbon emissions impose costs on society that aren't reflected in fossil fuel prices. This is a classic case where government intervention corrects market failure. Furthermore, historical precedent shows that government investment in emerging technologies, from the internet to GPS, has been crucial for innovation. Without subsidies, renewable energy cannot compete with fossil fuels that have benefited from decades of government support and don't pay for their environmental costs.

Speaker 2: The externality argument has merit, but subsidies are not the optimal solution. A carbon tax would directly address externalities without picking winners and losers in the energy market. Subsidies create inefficiencies by supporting technologies regardless of their actual performance or cost-effectiveness. Some renewable projects funded by subsidies have been spectacular failures, wasting taxpayer money. Instead of subsidizing specific technologies, we should establish a level playing field where all energy sources pay their true costs, including environmental impacts. This approach would drive innovation more effectively than bureaucratic allocation of resources.
""" 