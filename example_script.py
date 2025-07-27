#!/usr/bin/env python3
"""
Example script demonstrating the Debate Audio to Formal Logic Converter.

This script provides a command-line interface to process audio files
and generate formal logic analysis documents.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Import our modules
import config
from audio_processor import AudioProcessor
from logic_converter import LogicConverter
from document_generator import DocumentGenerator

def main():
    """Main example script function."""
    
    print("🎯 Debate Audio to Formal Logic Converter - Example Script")
    print("=" * 60)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert debate audio to formal logic arguments")
    parser.add_argument("--audio-file", "-f", type=str, help="Path to audio file to process")
    parser.add_argument("--critique", "-c", action="store_true", help="Include logical critiques")
    parser.add_argument("--model", "-m", type=str, default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Check API key
    if not config.ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Please create a .env file with your API key:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Set Whisper model
    config.WHISPER_MODEL = args.model
    
    if args.interactive or not args.audio_file:
        run_interactive_mode()
    else:
        process_single_file(args.audio_file, args.critique)

def run_interactive_mode():
    """Run the script in interactive mode."""
    
    print("\n🎵 Interactive Mode")
    print("-" * 30)
    
    # Show available sample files
    show_sample_files()
    
    # Get audio file path
    while True:
        print("\nOptions:")
        print("1. Enter path to your audio file")
        print("2. Use a sample file")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            file_path = input("Enter audio file path: ").strip()
            if os.path.exists(file_path):
                break
            else:
                print("❌ File not found. Please try again.")
        
        elif choice == "2":
            sample_files = get_sample_files()
            if not sample_files:
                print("❌ No sample files found.")
                continue
            
            print("\nAvailable sample files:")
            for i, file in enumerate(sample_files, 1):
                print(f"{i}. {file}")
            
            try:
                file_index = int(input("Select file number: ")) - 1
                if 0 <= file_index < len(sample_files):
                    file_path = os.path.join(config.SAMPLE_AUDIO_DIR, sample_files[file_index])
                    break
                else:
                    print("❌ Invalid selection.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
    
    # Get critique option
    critique_choice = input("\nInclude logical critiques? (y/n): ").strip().lower()
    include_critiques = critique_choice in ['y', 'yes', '1', 'true']
    
    # Process the file
    process_single_file(file_path, include_critiques)

def process_single_file(file_path: str, include_critiques: bool = False):
    """Process a single audio file through the complete pipeline."""
    
    print(f"\n🔄 Processing: {os.path.basename(file_path)}")
    print("-" * 50)
    
    try:
        # Initialize processors
        print("🔧 Loading AI models...")
        audio_processor = AudioProcessor()
        logic_converter = LogicConverter()
        document_generator = DocumentGenerator()
        
        # Step 1: Transcribe audio
        print("🎵 Transcribing audio with Whisper...")
        transcription_result = audio_processor.transcribe_audio(file_path)
        
        print(f"✅ Transcription complete!")
        print(f"   - Language detected: {transcription_result.get('language', 'Unknown')}")
        print(f"   - Speakers detected: {len(transcription_result.get('speakers', []))}")
        
        # Show transcription preview
        full_text = transcription_result.get("text", "")
        preview_length = 200
        preview = full_text[:preview_length] + "..." if len(full_text) > preview_length else full_text
        print(f"   - Preview: {preview}")
        
        # Step 2: Convert to formal logic
        print("\n🧠 Converting to formal logic arguments...")
        formal_arguments = logic_converter.convert_to_formal_logic(transcription_result)
        
        print("✅ Formal logic conversion complete!")
        
        # Show speakers and arguments
        speakers = formal_arguments.get("speakers", [])
        for speaker in speakers:
            speaker_data = formal_arguments["formal_arguments"].get(speaker, {})
            structured_args = speaker_data.get("structured_arguments", [])
            print(f"   - {speaker}: {len(structured_args)} arguments identified")
        
        # Step 3: Generate critiques if requested
        if include_critiques:
            print("\n🔍 Generating logical critiques...")
            formal_arguments = logic_converter.critique_arguments(formal_arguments, include_critiques=True)
            
            print("✅ Critique analysis complete!")
            
            # Show critique summary
            if "critiques" in formal_arguments:
                total_issues = 0
                for speaker, critique_data in formal_arguments["critiques"].items():
                    problems = critique_data.get("identified_problems", [])
                    total_issues += len(problems)
                    print(f"   - {speaker}: {len(problems)} logical issues identified")
                
                print(f"   - Total issues found: {total_issues}")
        
        # Step 4: Generate documents
        print("\n📄 Generating Word documents...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"debate_analysis_{timestamp}"
        
        generated_files = document_generator.generate_documents(
            formal_arguments,
            include_critiques=include_critiques,
            output_filename=base_filename
        )
        
        print("✅ Document generation complete!")
        
        # Show generated files
        print(f"\n📁 Generated files:")
        for file_path in generated_files:
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"   - {os.path.basename(file_path)} ({file_size:.1f} KB)")
            print(f"     Full path: {file_path}")
        
        print(f"\n🎉 Analysis complete! Check the '{config.OUTPUT_DIR}' directory for your documents.")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        print("\n🔧 Technical details:")
        print(traceback.format_exc())

def show_sample_files():
    """Display information about available sample files."""
    
    sample_files = get_sample_files()
    
    if sample_files:
        print(f"\n📋 Sample files available in '{config.SAMPLE_AUDIO_DIR}':")
        for file in sample_files:
            file_path = os.path.join(config.SAMPLE_AUDIO_DIR, file)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"   - {file} ({file_size:.1f} MB)")
    else:
        print(f"\n📋 No sample files found in '{config.SAMPLE_AUDIO_DIR}'")
        print("   Add some sample audio files to test the system!")

def get_sample_files():
    """Get list of sample audio files."""
    
    if not os.path.exists(config.SAMPLE_AUDIO_DIR):
        return []
    
    sample_files = []
    for file in os.listdir(config.SAMPLE_AUDIO_DIR):
        if file.lower().endswith(tuple(config.SUPPORTED_AUDIO_FORMATS)):
            sample_files.append(file)
    
    return sorted(sample_files)

def create_sample_audio_file():
    """Create a sample audio file for testing (placeholder)."""
    
    sample_dir = Path(config.SAMPLE_AUDIO_DIR)
    sample_dir.mkdir(exist_ok=True)
    
    # Create a text file with sample content instead of actual audio
    sample_file = sample_dir / "sample_debate_instructions.txt"
    
    sample_content = """
Sample Debate Audio Instructions
===============================

To test this system, you need actual audio files of debates or discussions.

Here are some suggestions for sample content:

1. Record a short debate between two people on any topic
2. Download debate audio from public sources (with proper permissions)
3. Use text-to-speech to create sample debate audio from scripts
4. Find educational debate recordings in the public domain

Supported formats: MP3, WAV, M4A, FLAC, OGG, WMA

Place your sample audio files in this directory (sample_audio/) and run:
python example_script.py --interactive

Or use the Streamlit app:
streamlit run streamlit_app.py
"""
    
    with open(sample_file, 'w') as f:
        f.write(sample_content)
    
    print(f"📝 Created sample instructions file: {sample_file}")

if __name__ == "__main__":
    # Create sample directory and instructions if it doesn't exist
    if not os.path.exists(config.SAMPLE_AUDIO_DIR):
        create_sample_audio_file()
    
    main() 