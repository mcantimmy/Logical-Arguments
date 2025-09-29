import streamlit as st
import os
import tempfile
import traceback
from datetime import datetime
import config
from audio_processor import AudioProcessor
from logic_converter import LogicConverter
from document_generator import DocumentGenerator

# Configure Streamlit page
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_audio_processor():
    """Load and cache the audio processor."""
    return AudioProcessor()

@st.cache_resource
def load_logic_converter():
    """Load and cache the logic converter."""
    try:
        return LogicConverter()
    except ValueError as e:
        st.error(f"Error initializing Logic Converter: {e}")
        st.error("Please set your ANTHROPIC_API_KEY environment variable.")
        return None

@st.cache_resource
def load_document_generator():
    """Load and cache the document generator."""
    return DocumentGenerator()

def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("🎯 Debate Audio to Formal Logic Converter")
    st.markdown("""
    This application converts debate audio files into formal logic arguments using AI transcription and analysis.
    
    **Features:**
    - 🎵 Audio transcription with speaker detection
    - 🧠 Formal logic argument extraction using Claude AI
    - 📄 Professional Word document generation
    - 🔍 Optional logical critique and error highlighting
    """)
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # API Key status
    api_key_status = "✅ Configured" if config.ANTHROPIC_API_KEY else "❌ Missing"
    st.sidebar.markdown(f"**Anthropic API Key:** {api_key_status}")
    
    if not config.ANTHROPIC_API_KEY:
        st.sidebar.error("Please set ANTHROPIC_API_KEY environment variable")
        st.sidebar.markdown("Create a `.env` file with: `ANTHROPIC_API_KEY=your_api_key_here`")
    
    # Processing options
    st.sidebar.header("Processing Options")
    include_critiques = st.sidebar.checkbox(
        "Include Logical Critiques", 
        value=False,
        help="Generate critique analysis highlighting logical flaws and inconsistencies"
    )
    
    # Store in session state for use by sample file processing
    st.session_state['include_critiques'] = include_critiques
    
    whisper_model = st.sidebar.selectbox(
        "Whisper Model Size",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
        help="Larger models are more accurate but slower"
    )
    
    # Update model in config
    config.WHISPER_MODEL = whisper_model
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload Audio File")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'wma'],
            help=f"Supported formats: {', '.join(config.SUPPORTED_AUDIO_FORMATS)}"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            st.info(f"**File:** {uploaded_file.name} ({file_size:.1f} MB)")
            
            if file_size > config.MAX_FILE_SIZE / (1024 * 1024):
                st.error(f"File too large. Maximum size: {config.MAX_FILE_SIZE / (1024 * 1024)} MB")
                return
            
            # Audio player
            st.audio(uploaded_file.getvalue(), format=uploaded_file.type)
    
    with col2:
        st.header("🚀 Process Audio")
        
        if uploaded_file is not None and config.ANTHROPIC_API_KEY:
            if st.button("Start Analysis", type="primary", use_container_width=True):
                process_audio_file(uploaded_file, include_critiques)
        elif not config.ANTHROPIC_API_KEY:
            st.error("API key required to process audio")
        else:
            st.info("Upload an audio file to begin")
    
    # Sample files section
    st.header("📋 Sample Files")
    show_sample_files()
    
    # Instructions section
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. **Set up API Key**: Create a `.env` file in the project directory with your Anthropic API key:
           ```
           ANTHROPIC_API_KEY=your_api_key_here
           ```
        
        2. **Upload Audio**: Click "Browse files" and select your debate audio file
        
        3. **Configure Options**: 
           - Toggle "Include Logical Critiques" to analyze arguments for logical flaws
           - Select Whisper model size (larger = more accurate but slower)
        
        4. **Process**: Click "Start Analysis" to begin processing
        
        5. **Download**: Once complete, download the generated Word documents
        
        **Supported Audio Formats:** MP3, WAV, M4A, FLAC, OGG, WMA
        
        **Output:** 
        - Clean document with formal logic arguments by speaker
        - Critique document (if enabled) with highlighted logical issues
        """)

def process_audio_file(uploaded_file, include_critiques):
    """Process the uploaded audio file through the complete pipeline."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Step 1: Load processors
        status_text.text("🔧 Loading AI models...")
        progress_bar.progress(10)
        
        audio_processor = load_audio_processor()
        logic_converter = load_logic_converter()
        document_generator = load_document_generator()
        
        if not logic_converter:
            st.error("Failed to initialize Logic Converter. Check your API key.")
            return
        
        # Step 2: Transcribe audio
        status_text.text("🎵 Transcribing audio...")
        progress_bar.progress(30)
        
        with st.spinner("Transcribing audio with Whisper..."):
            transcription_result = audio_processor.transcribe_audio(temp_path)
        
        # Display transcription preview
        st.success("✅ Audio transcribed successfully!")
        
        with st.expander("👀 View Transcription"):
            st.text_area("Full Transcript", transcription_result["text"], height=200)
            
            # Show speakers
            speakers = transcription_result.get("speakers", [])
            st.write(f"**Detected Speakers:** {', '.join(speakers)}")
        
        # Step 3: Convert to formal logic
        status_text.text("🧠 Converting to formal logic arguments...")
        progress_bar.progress(60)
        
        with st.spinner("Analyzing arguments with Claude AI..."):
            formal_arguments = logic_converter.convert_to_formal_logic(transcription_result)
        
        # Step 4: Generate critiques if requested
        if include_critiques:
            status_text.text("🔍 Analyzing logical consistency...")
            progress_bar.progress(80)
            
            with st.spinner("Generating logical critiques..."):
                formal_arguments = logic_converter.critique_arguments(formal_arguments, include_critiques=True)
        
        # Step 5: Generate documents
        status_text.text("📄 Generating Word documents...")
        progress_bar.progress(90)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"debate_analysis_{timestamp}"
        
        with st.spinner("Creating Word documents..."):
            generated_files = document_generator.generate_documents(
                formal_arguments, 
                include_critiques=include_critiques,
                output_filename=base_filename
            )
        
        # Step 6: Complete
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display results
        display_results(formal_arguments, generated_files, include_critiques)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
    except Exception as e:
        st.error(f"❌ Error processing audio: {str(e)}")
        st.error("Please check your API key and try again.")
        
        # Show detailed error in expander
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())

def display_results(formal_arguments, generated_files, include_critiques):
    """Display the analysis results and download links."""
    
    st.header("📊 Analysis Results")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        speakers = formal_arguments.get("speakers", [])
        st.metric("Speakers Detected", len(speakers))
    
    with col2:
        total_args = 0
        for speaker_args in formal_arguments.get("formal_arguments", {}).values():
            structured_args = speaker_args.get("structured_arguments", [])
            total_args += len(structured_args)
        st.metric("Arguments Identified", total_args)
    
    with col3:
        if include_critiques and "critiques" in formal_arguments:
            total_issues = 0
            for critique in formal_arguments["critiques"].values():
                problems = critique.get("identified_problems", [])
                total_issues += len(problems)
            st.metric("Logical Issues Found", total_issues)
        else:
            st.metric("Critiques", "Disabled")
    
    # Speaker breakdown
    st.subheader("🗣️ Speaker Analysis")
    
    for speaker in formal_arguments.get("speakers", []):
        with st.expander(f"View {speaker} Analysis"):
            speaker_data = formal_arguments["formal_arguments"].get(speaker, {})
            
            # Original text
            st.markdown("**Original Text:**")
            st.write(speaker_data.get("original_text", "No text available"))
            
            # Formal analysis preview
            st.markdown("**Formal Logic Analysis (Preview):**")
            raw_analysis = speaker_data.get("raw_analysis", "")
            preview = raw_analysis[:500] + "..." if len(raw_analysis) > 500 else raw_analysis
            st.write(preview)
            
            # Critique preview if available
            if include_critiques and "critiques" in formal_arguments:
                critique_data = formal_arguments["critiques"].get(speaker, {})
                problems = critique_data.get("identified_problems", [])
                
                if problems:
                    st.markdown("**Logical Issues Identified:**")
                    for i, problem in enumerate(problems[:3], 1):  # Show first 3
                        st.warning(f"**Issue {i}:** {problem.get('description', 'No description')[:100]}...")
                    
                    if len(problems) > 3:
                        st.info(f"... and {len(problems) - 3} more issues. See full document for details.")
    
    # Download section
    st.subheader("📥 Download Documents")
    
    for file_path in generated_files:
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            # Determine document type for button label
            if "critique" in filename.lower():
                label = "📄 Download Document with Critiques"
                help_text = "Word document with arguments and highlighted logical issues"
            else:
                label = "📄 Download Clean Document"
                help_text = "Word document with formal logic arguments only"
            
            st.download_button(
                label=label,
                data=file_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                help=help_text,
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error preparing download for {filename}: {e}")

def process_sample_file(file_path: str, filename: str):
    """Process a sample audio file through the complete pipeline."""
    
    # Get the current critique setting from the sidebar
    include_critiques = st.session_state.get('include_critiques', False)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Load processors
        status_text.text("🔧 Loading AI models...")
        progress_bar.progress(10)
        
        audio_processor = load_audio_processor()
        logic_converter = load_logic_converter()
        document_generator = load_document_generator()
        
        if not logic_converter:
            st.error("Failed to initialize Logic Converter. Check your API key.")
            return
        
        # Step 2: Transcribe audio
        status_text.text("🎵 Transcribing audio...")
        progress_bar.progress(30)
        
        with st.spinner("Transcribing audio with Whisper..."):
            transcription_result = audio_processor.transcribe_audio(file_path)
        
        # Display transcription preview
        st.success("✅ Audio transcribed successfully!")
        
        with st.expander("👀 View Transcription"):
            st.text_area("Full Transcript", transcription_result["text"], height=200)
            
            # Show speakers
            speakers = transcription_result.get("speakers", [])
            st.write(f"**Detected Speakers:** {', '.join(speakers)}")
        
        # Step 3: Convert to formal logic
        status_text.text("🧠 Converting to formal logic arguments...")
        progress_bar.progress(60)
        
        with st.spinner("Analyzing arguments with Claude AI..."):
            formal_arguments = logic_converter.convert_to_formal_logic(transcription_result)
        
        # Step 4: Generate critiques if requested
        if include_critiques:
            status_text.text("🔍 Analyzing logical consistency...")
            progress_bar.progress(80)
            
            with st.spinner("Generating logical critiques..."):
                formal_arguments = logic_converter.critique_arguments(formal_arguments, include_critiques=True)
        
        # Step 5: Generate documents
        status_text.text("📄 Generating Word documents...")
        progress_bar.progress(90)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"sample_analysis_{timestamp}"
        
        with st.spinner("Creating Word documents..."):
            generated_files = document_generator.generate_documents(
                formal_arguments, 
                include_critiques=include_critiques,
                output_filename=base_filename
            )
        
        # Step 6: Complete
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display results
        display_results(formal_arguments, generated_files, include_critiques)
        
    except Exception as e:
        st.error(f"❌ Error processing audio: {str(e)}")
        st.error("Please check your API key and try again.")
        
        # Show detailed error in expander
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())

def show_sample_files():
    """Display information about sample files and allow processing them."""
    
    sample_dir = config.SAMPLE_AUDIO_DIR
    
    if os.path.exists(sample_dir):
        sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(tuple(config.SUPPORTED_AUDIO_FORMATS))]
        
        if sample_files:
            st.write("Sample audio files available:")
            
            # Create columns for file display and processing buttons
            for file in sample_files:
                file_path = os.path.join(sample_dir, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"• {file} ({file_size:.1f} MB)")
                
                with col2:
                    # Play button for sample file
                    try:
                        with open(file_path, "rb") as audio_file:
                            audio_data = audio_file.read()
                        st.audio(audio_data, format="audio/wav")
                    except Exception as e:
                        st.error(f"Error loading {file}")
                
                with col3:
                    # Process button for sample file
                    if config.ANTHROPIC_API_KEY:
                        if st.button(f"Process", key=f"process_{file}", help=f"Process {file}"):
                            process_sample_file(file_path, file)
                    else:
                        st.error("API key required")
        else:
            st.info("No sample files found. Add audio files to the `sample_audio/` directory.")
    else:
        st.info("Sample audio directory not found. Create `sample_audio/` directory and add sample files.")

if __name__ == "__main__":
    main() 