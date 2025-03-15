import os
import speech_recognition as sr
import tempfile
import logging
from typing import Dict, Any, Optional
from pydub import AudioSegment

# Set up logging
logger = logging.getLogger(__name__)

def convert_audio_to_text(audio_file_path: str) -> Dict[str, Any]:
    """
    Convert audio file to text using SpeechRecognition library.
    
    Args:
        audio_file_path: Path to the audio file
    
    Returns:
        Dictionary containing status and either the transcribed text or error message
    """
    recognizer = sr.Recognizer()
    
    try:
        # Try to convert the audio file to WAV format if it's not already
        converted_file_path = ensure_wav_format(audio_file_path)
        file_to_use = converted_file_path or audio_file_path
        
        logger.info(f"Processing audio file: {file_to_use}")
        
        # Load the audio file
        with sr.AudioFile(file_to_use) as source:
            # Record the audio data from the source
            logger.info("Recording audio data from source")
            audio_data = recognizer.record(source)
            
            # Try multiple recognition engines
            try:
                logger.info("Attempting recognition with Sphinx")
                # First try Sphinx (offline) 
                text = recognizer.recognize_sphinx(audio_data)
                logger.info(f"Sphinx recognition successful: {text}")
                return {"status": "success", "text": text}
            except sr.UnknownValueError:
                logger.warning("Sphinx could not understand audio")
                try:
                    # Fall back to Google (requires internet)
                    logger.info("Attempting recognition with Google Speech Recognition")
                    text = recognizer.recognize_google(audio_data)
                    logger.info(f"Google recognition successful: {text}")
                    return {"status": "success", "text": text}
                except sr.UnknownValueError:
                    return {"status": "error", "message": "Speech recognition could not understand audio"}
                except sr.RequestError as e:
                    logger.error(f"Google recognition error: {e}")
                    return {"status": "error", "message": f"Google Speech Recognition error: {e}"}
            except sr.RequestError as e:
                logger.error(f"Sphinx error: {e}")
                try:
                    # Try Google if Sphinx fails
                    logger.info("Sphinx failed, trying Google Speech Recognition")
                    text = recognizer.recognize_google(audio_data)
                    logger.info(f"Google recognition successful: {text}")
                    return {"status": "success", "text": text}
                except Exception as inner_e:
                    logger.error(f"Google recognition error: {inner_e}")
                    return {"status": "error", "message": f"Speech recognition failed: {e}. Fallback also failed."}
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Error processing audio: {str(e)}"}
    finally:
        # Clean up any temporary converted file
        if converted_file_path and converted_file_path != audio_file_path and os.path.exists(converted_file_path):
            try:
                os.remove(converted_file_path)
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {str(e)}")


def ensure_wav_format(file_path: str) -> Optional[str]:
    """
    Ensure the audio file is in WAV format. If not, convert it.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Path to the WAV file (either original or converted), or None if conversion failed
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # If already a WAV file, return None to indicate no conversion needed
        if file_ext == '.wav':
            return None
            
        logger.info(f"Converting {file_ext} file to WAV format")
        
        # Create temporary file for the converted WAV
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav.close()
        
        # Convert using pydub
        if file_ext == '.webm':
            # For webm files from browser recording
            audio = AudioSegment.from_file(file_path, format="webm")
        elif file_ext == '.ogg':
            audio = AudioSegment.from_ogg(file_path)
        elif file_ext == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
        else:
            # Try generic conversion
            audio = AudioSegment.from_file(file_path)
            
        # Export as WAV
        audio.export(temp_wav.name, format="wav")
        logger.info(f"Converted audio file saved to {temp_wav.name}")
        
        return temp_wav.name
    except Exception as e:
        logger.error(f"Error converting audio format: {str(e)}", exc_info=True)
        return None


def save_uploaded_file(audio_file, file_extension: str = ".wav") -> Optional[str]:
    """
    Save an uploaded audio file temporarily for processing.
    
    Args:
        audio_file: UploadedFile object
        file_extension: Extension of the audio file
    
    Returns:
        Path to the saved temporary file or None if failed
    """
    try:
        # Create a temporary file to store the uploaded audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        
        # Write chunks of the file to the temporary file
        for chunk in audio_file.chunks():
            temp_file.write(chunk)
        
        temp_file.close()
        logger.info(f"Uploaded audio saved to {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}", exc_info=True)
        return None
