# 🎯 Debate Audio to Formal Logic Converter

A comprehensive Python application that converts debate audio files into structured formal logic arguments using AI transcription and analysis. The system automatically transcribes speech, identifies speakers, converts arguments to formal logic notation, and optionally critiques logical consistency.

## ✨ Features

- 🎵 **Audio Transcription**: Automatic speech-to-text using OpenAI Whisper with speaker detection
- 🧠 **Formal Logic Conversion**: Convert natural language arguments to formal logic using Claude AI
- 📄 **Document Generation**: Professional Word documents with structured argument analysis
- 🔍 **Logical Critique**: Optional analysis highlighting logical fallacies and inconsistencies
- 🖥️ **Streamlit UI**: User-friendly web interface for easy processing
- 📱 **Command Line Interface**: Example script for batch processing and automation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com/))
- FFmpeg (for audio processing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Logical-Arguments
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the template and edit with your API key
   cp env_template.txt .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📖 Usage

### Web Interface (Streamlit)

1. **Start the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Upload audio file:**
   - Supported formats: MP3, WAV, M4A, FLAC, OGG, WMA
   - Maximum file size: 100MB

3. **Configure options:**
   - Toggle "Include Logical Critiques" for error analysis
   - Select Whisper model size (larger = more accurate but slower)

4. **Process and download:**
   - Click "Start Analysis" to begin processing
   - Download generated Word documents when complete

### Command Line Interface

**Interactive mode:**
```bash
python example_script.py --interactive
```

**Process specific file:**
```bash
python example_script.py --audio-file path/to/debate.mp3 --critique
```

**Available options:**
- `--audio-file, -f`: Path to audio file
- `--critique, -c`: Include logical critiques
- `--model, -m`: Whisper model size (tiny/base/small/medium/large)
- `--interactive, -i`: Interactive mode

## 📁 Project Structure

```
Logical-Arguments/
├── audio_processor.py       # Audio transcription with Whisper
├── logic_converter.py       # Claude AI integration for logic analysis
├── document_generator.py    # Word document generation
├── streamlit_app.py        # Web interface
├── example_script.py       # Command-line example
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── env_template.txt       # Environment variable template
├── sample_audio/         # Directory for sample audio files
├── output/              # Generated documents directory
└── README.md           # This file
```

## 🎵 Supported Audio Formats

- **MP3** - Most common format
- **WAV** - Uncompressed audio
- **M4A** - Apple/iTunes format
- **FLAC** - Lossless compression
- **OGG** - Open source format
- **WMA** - Windows Media Audio

## 📄 Output Documents

The system generates professional Word documents with:

### Clean Document
- **Document metadata** (generation time, speakers, language)
- **Formal logic analysis** organized by speaker
- **Structured argument breakdown** (premises, conclusions, logical structure)
- **Original transcription appendix** with timestamps

### Critique Document (Optional)
- All content from clean document
- **Highlighted logical issues** marked in red
- **Detailed critique analysis** for each speaker
- **Overall critique summary** with issue statistics
- **Problem categorization** by severity and type

## 🧠 AI Analysis Features

### Formal Logic Conversion
- Identifies main arguments and supporting premises
- Converts to formal logical notation (∧, ∨, →, ¬, ∀, ∃)
- Classifies argument types (deductive, inductive, abductive)
- Notes supporting evidence and authorities cited

### Logical Critique (Optional)
- **Logical Fallacies**: Ad hominem, straw man, false dichotomy, etc.
- **Invalid Inferences**: Conclusions that don't follow from premises
- **Missing Premises**: Implicit assumptions that should be explicit
- **Contradictions**: Internal inconsistencies within arguments
- **Weak Evidence**: Claims lacking sufficient support
- **Structural Issues**: Problems with argument organization

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Anthropic Claude API Key
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Whisper model size (default: base)
WHISPER_MODEL=base

# Optional: Maximum file size in bytes (default: 100MB)
MAX_FILE_SIZE=104857600
```

### Whisper Model Options

- **tiny**: Fastest, least accurate (~39 MB)
- **base**: Good balance of speed and accuracy (~74 MB) - **Default**
- **small**: Better accuracy (~244 MB)
- **medium**: High accuracy (~769 MB)
- **large**: Highest accuracy (~1550 MB)

## 🛠️ Development

### Adding Sample Audio Files

1. Create audio files of debates or discussions
2. Place them in the `sample_audio/` directory
3. Supported formats: MP3, WAV, M4A, FLAC, OGG, WMA

### Extending the System

The modular design makes it easy to extend:

- **Audio Processing**: Modify `AudioProcessor` class for better speaker detection
- **Logic Analysis**: Enhance `LogicConverter` prompts for domain-specific analysis
- **Document Generation**: Customize `DocumentGenerator` for different output formats
- **UI**: Extend `streamlit_app.py` for additional features

## 🔧 Troubleshooting

### Common Issues

**API Key Error:**
```
Error: ANTHROPIC_API_KEY environment variable not set
```
- Solution: Create `.env` file with your Anthropic API key

**Audio Format Error:**
```
Unsupported audio format
```
- Solution: Convert audio to supported format (MP3, WAV, etc.)

**Memory Issues with Large Models:**
```
CUDA out of memory / RAM insufficient
```
- Solution: Use smaller Whisper model (tiny/base instead of large)

**FFmpeg Not Found:**
```
ffmpeg not found
```
- Solution: Install FFmpeg for your operating system

### Performance Tips

- Use **base** or **small** Whisper models for faster processing
- Keep audio files under 10 minutes for optimal performance
- Ensure good audio quality for better transcription accuracy
- Use **critique mode** only when needed (slower processing)

## 📊 Example Output

### Speaker Analysis Sample
```
Speaker 1: Argument Analysis
==========================

Original Statement:
"All renewable energy sources are environmentally friendly. Solar power is a renewable energy source. Therefore, solar power is environmentally friendly."

Formal Logic Analysis:
Argument 1: Syllogistic Reasoning
- Premise 1: ∀x (RenewableEnergy(x) → EnvironmentallyFriendly(x))
- Premise 2: RenewableEnergy(SolarPower)
- Conclusion: EnvironmentallyFriendly(SolarPower)
- Structure: Valid deductive syllogism (Modus Ponens)
- Type: Deductive reasoning
```

### Critique Sample (if enabled)
```
⚠️ Logical Issues Identified:

Problem 1: Overgeneralization
The premise "All renewable energy sources are environmentally friendly" 
may be too broad and lacks nuance regarding manufacturing impacts.
Severity: Moderate
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Documentation**: Check this README for detailed usage instructions
- **API**: Review Anthropic Claude API documentation for advanced features

---

**Built with ❤️ using OpenAI Whisper, Anthropic Claude, and Streamlit**

