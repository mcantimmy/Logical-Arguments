import anthropic
from typing import Dict, List, Optional
import config
import json

class LogicConverter:
    """Converts transcribed debate speech into formal logic arguments using Claude."""
    
    def __init__(self, api_key: str = None):
        """Initialize the logic converter with Anthropic API key."""
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def convert_to_formal_logic(self, transcription_data: Dict) -> Dict:
        """
        Convert transcribed debate into formal logic arguments.
        
        Args:
            transcription_data: Dictionary containing transcription results from AudioProcessor
            
        Returns:
            Dictionary containing formal logic arguments organized by speaker
        """
        segments = transcription_data.get("segments", [])
        speakers = transcription_data.get("speakers", [])
        
        # Group segments by speaker
        speaker_texts = self._group_by_speaker(segments)
        
        # Convert each speaker's arguments to formal logic
        formal_arguments = {}
        
        for speaker, text_segments in speaker_texts.items():
            combined_text = " ".join([segment["text"] for segment in text_segments])
            
            formal_logic = self._convert_speaker_arguments(speaker, combined_text)
            formal_arguments[speaker] = formal_logic
        
        return {
            "speakers": speakers,
            "formal_arguments": formal_arguments,
            "original_transcription": transcription_data
        }
    
    def _group_by_speaker(self, segments: List[Dict]) -> Dict[str, List[Dict]]:
        """Group transcript segments by speaker."""
        speaker_segments = {}
        
        for segment in segments:
            speaker = segment.get("speaker", "Unknown")
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            speaker_segments[speaker].append(segment)
        
        return speaker_segments
    
    def _convert_speaker_arguments(self, speaker: str, text: str) -> Dict:
        """Convert a speaker's text into formal logic arguments."""
        
        prompt = f"""You are an expert in formal logic and argumentation. Your task is to analyze the following debate speech and convert it into formal logical arguments.

Speaker: {speaker}
Speech Text: {text}

Please analyze this speech and provide:

1. **Main Arguments**: Identify the primary arguments made by this speaker
2. **Premises**: List the premises (supporting statements) for each argument
3. **Conclusions**: State the conclusions drawn from the premises
4. **Logical Structure**: Present each argument in formal logical notation where possible (using propositional logic symbols like ∧, ∨, →, ¬, ∀, ∃)
5. **Argument Types**: Classify the types of arguments used (deductive, inductive, abductive, etc.)
6. **Supporting Evidence**: Note any evidence, examples, or authorities cited

Format your response as a structured analysis that clearly separates each argument and its components. Use clear, formal language appropriate for logical analysis.

If the speech contains multiple distinct arguments, number them (Argument 1, Argument 2, etc.) and analyze each separately.

If the speech contains fallacies or weak reasoning, note this in your analysis but do not critique - simply present the logical structure as intended by the speaker."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis = response.content[0].text
            
            # Parse the response to extract structured data
            structured_analysis = self._parse_logic_analysis(analysis)
            
            return {
                "raw_analysis": analysis,
                "structured_arguments": structured_analysis,
                "speaker": speaker,
                "original_text": text
            }
            
        except Exception as e:
            print(f"Error converting arguments to formal logic: {e}")
            return {
                "error": str(e),
                "speaker": speaker,
                "original_text": text
            }
    
    def _parse_logic_analysis(self, analysis: str) -> List[Dict]:
        """Parse the Claude response to extract structured argument data."""
        # This is a simplified parser - in a production system, you might want more sophisticated parsing
        arguments = []
        
        # Split by argument sections
        sections = analysis.split("Argument ")
        
        for i, section in enumerate(sections):
            if i == 0 or not section.strip():  # Skip intro text
                continue
                
            arg_data = {
                "argument_number": i,
                "premises": [],
                "conclusions": [],
                "logical_structure": "",
                "argument_type": "",
                "supporting_evidence": "",
                "full_text": section.strip()
            }
            
            # Simple extraction of key components
            lines = section.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "premises:" in line.lower() or "premise:" in line.lower():
                    current_section = "premises"
                elif "conclusion:" in line.lower():
                    current_section = "conclusions"
                elif "logical structure:" in line.lower():
                    current_section = "logical_structure"
                elif "argument type:" in line.lower():
                    current_section = "argument_type"
                elif "supporting evidence:" in line.lower():
                    current_section = "supporting_evidence"
                else:
                    # Add content to current section
                    if current_section == "premises" and line.startswith(('-', '•', '*')):
                        arg_data["premises"].append(line[1:].strip())
                    elif current_section == "conclusions" and line.startswith(('-', '•', '*')):
                        arg_data["conclusions"].append(line[1:].strip())
                    elif current_section == "logical_structure":
                        arg_data["logical_structure"] += line + " "
                    elif current_section == "argument_type":
                        arg_data["argument_type"] += line + " "
                    elif current_section == "supporting_evidence":
                        arg_data["supporting_evidence"] += line + " "
            
            # Clean up strings
            for key in ["logical_structure", "argument_type", "supporting_evidence"]:
                arg_data[key] = arg_data[key].strip()
            
            arguments.append(arg_data)
        
        return arguments
    
    def critique_arguments(self, formal_arguments: Dict, include_critiques: bool = True) -> Dict:
        """
        Critique the formal logic arguments for logical flaws and inconsistencies.
        
        Args:
            formal_arguments: Dictionary containing formal logic arguments
            include_critiques: Whether to include detailed critiques
            
        Returns:
            Dictionary containing critiques and highlighted problems
        """
        if not include_critiques:
            return formal_arguments
        
        critiqued_arguments = {}
        
        for speaker, arguments in formal_arguments["formal_arguments"].items():
            critique_result = self._critique_speaker_arguments(speaker, arguments)
            critiqued_arguments[speaker] = critique_result
        
        return {
            "speakers": formal_arguments["speakers"],
            "formal_arguments": formal_arguments["formal_arguments"],
            "critiques": critiqued_arguments,
            "original_transcription": formal_arguments["original_transcription"]
        }
    
    def _critique_speaker_arguments(self, speaker: str, arguments: Dict) -> Dict:
        """Critique a specific speaker's arguments for logical flaws."""
        
        raw_analysis = arguments.get("raw_analysis", "")
        
        prompt = f"""You are an expert in formal logic, critical thinking, and argumentation analysis. Your task is to critique the following formal logic arguments for logical flaws, fallacies, and inconsistencies.

Speaker: {speaker}
Arguments Analysis:
{raw_analysis}

Please provide a detailed critique focusing on:

1. **Logical Fallacies**: Identify any formal or informal fallacies (ad hominem, straw man, false dichotomy, etc.)
2. **Invalid Inferences**: Point out conclusions that don't logically follow from premises
3. **Missing Premises**: Identify implicit assumptions that should be stated explicitly
4. **Contradictions**: Note any internal contradictions within the arguments
5. **Weak Evidence**: Highlight claims that lack sufficient supporting evidence
6. **Structural Issues**: Point out problems with argument structure or logical flow

For each problem identified:
- **Problem Type**: Classify the type of logical issue
- **Location**: Specify which argument or statement contains the problem
- **Explanation**: Explain why this is logically problematic
- **Severity**: Rate the severity (Minor, Moderate, Major, Critical)

Be thorough but fair in your analysis. Focus on logical structure rather than content agreement."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            critique = response.content[0].text
            
            # Parse critique to identify specific problems
            problems = self._parse_critique_problems(critique)
            
            return {
                "raw_critique": critique,
                "identified_problems": problems,
                "speaker": speaker
            }
            
        except Exception as e:
            print(f"Error critiquing arguments: {e}")
            return {
                "error": str(e),
                "speaker": speaker
            }
    
    def _parse_critique_problems(self, critique: str) -> List[Dict]:
        """Parse critique response to extract specific logical problems."""
        problems = []
        
        # Simple parsing to identify problem statements
        lines = critique.split('\n')
        current_problem = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for problem indicators
            if any(keyword in line.lower() for keyword in ['fallacy', 'invalid', 'contradiction', 'problem', 'issue', 'flaw']):
                if current_problem:
                    problems.append(current_problem)
                
                current_problem = {
                    "problem_type": "Logical Issue",
                    "description": line,
                    "severity": "Moderate",
                    "location": "General"
                }
            elif current_problem and line.startswith(('-', '•', '*')):
                current_problem["description"] += f" {line[1:].strip()}"
        
        # Add the last problem if it exists
        if current_problem:
            problems.append(current_problem)
        
        return problems 