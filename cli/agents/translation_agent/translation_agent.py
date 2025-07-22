import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect
import streamlit as st
import logging
import re
import unicodedata

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MTVlYzJiZi0yZTJmLTQ1YTYtOWM5NC0yMzI3ZjBhNmEwZmYiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjRhNmU2MzRkLWFmNGQtNDUwNy1hY2NmLWRjYjcxYzU4ZGJlMCJ9._cDCMMUaZFqRDqQtfw8xShTe3DokUe7SBQ26C1UoXNg" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationAgent:
    def __init__(self):
        """Initialize the Translation Agent with multilingual models"""
        # Force CPU usage to avoid CUDA errors
        self.device = "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Language mapping for better user experience
        self.language_map = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'tr': 'Turkish',
            'pl': 'Polish',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'mt': 'Maltese',
            'ga': 'Irish',
            'cy': 'Welsh',
            'eu': 'Basque',
            'ca': 'Catalan',
            'gl': 'Galician',
            'is': 'Icelandic',
            'mk': 'Macedonian',
            'sq': 'Albanian',
            'be': 'Belarusian',
            'uk': 'Ukrainian',
            'he': 'Hebrew',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'tl': 'Filipino',
            'sw': 'Swahili',
            'am': 'Amharic',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'ne': 'Nepali',
            'or': 'Odia',
            'pa': 'Punjabi',
            'si': 'Sinhala',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ur': 'Urdu',
            'my': 'Myanmar',
            'km': 'Khmer',
            'lo': 'Lao',
            'ka': 'Georgian',
            'hy': 'Armenian',
            'az': 'Azerbaijani',
            'kk': 'Kazakh',
            'ky': 'Kyrgyz',
            'mn': 'Mongolian',
            'tg': 'Tajik',
            'tk': 'Turkmen',
            'uz': 'Uzbek',
            'fa': 'Persian',
            'ps': 'Pashto',
            'sd': 'Sindhi',
            'so': 'Somali',
            'xh': 'Xhosa',
            'zu': 'Zulu',
            'af': 'Afrikaans'
        }
        
        # RTL (Right-to-Left) languages that need special handling
        self.rtl_languages = {'ar', 'he', 'fa', 'ur', 'ps', 'sd'}
        
        # Languages that use complex scripts
        self.complex_script_languages = {'ar', 'hi', 'ur', 'bn', 'gu', 'kn', 'ml', 'mr', 'ne', 'or', 'pa', 'si', 'ta', 'te', 'th', 'my', 'km', 'lo'}
        
        self.translator = None
        self.tokenizer = None
        self.model_name = "facebook/mbart-large-50-many-to-many-mmt"
        self.max_chunk_length = 200  # Reduced for better handling of complex scripts
        self._load_model()
    
    def _load_model(self):
        """Load the translation model"""
        try:
            logger.info(f"Loading translation model: {self.model_name}")
            # Force CPU usage and use float32 for better compatibility
            self.translator = pipeline(
                "translation",
                model=self.model_name,
                device=-1,  # Force CPU usage
                torch_dtype=torch.float32,
                model_kwargs={"low_cpu_mem_usage": True}
            )
            
            # Load tokenizer separately for text chunking
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Translation model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to a smaller, more compatible model
            self.model_name = "Helsinki-NLP/opus-mt-mul-en"
            try:
                self.translator = pipeline(
                    "translation",
                    model=self.model_name,
                    device=-1,  # Force CPU usage
                    torch_dtype=torch.float32
                )
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                logger.info("Fallback model loaded successfully")
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                raise Exception("Could not load any translation model")
    
    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            # Clean text for better detection
            cleaned_text = self._clean_text_for_detection(text)
            # Use only first 1000 characters for detection to avoid issues
            sample_text = cleaned_text[:1000] if len(cleaned_text) > 1000 else cleaned_text
            detected_lang = detect(sample_text)
            return detected_lang
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"  # Default to English
    
    def _clean_text_for_detection(self, text):
        """Clean text for better language detection"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might confuse detection
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F\u0D80-\u0DFF\u0E00-\u0E7F\u0E80-\u0EFF\u0F00-\u0FFF\u1000-\u109F\u10A0-\u10FF\u1100-\u11FF\u1200-\u137F\u13A0-\u13FF\u1400-\u167F\u1680-\u169F\u16A0-\u16FF\u1700-\u171F\u1720-\u173F\u1740-\u175F\u1760-\u177F\u1780-\u17FF\u1800-\u18AF\u1900-\u194F\u1950-\u197F\u1980-\u19DF\u19E0-\u19FF\u1A00-\u1A1F\u1A20-\u1AAF\u1B00-\u1B7F\u1B80-\u1BBF\u1BC0-\u1BFF\u1C00-\u1C4F\u1C50-\u1C7F\u1C80-\u1C8F\u1CC0-\u1CCF\u1CD0-\u1CFF\u1D00-\u1D7F\u1D80-\u1DBF\u1DC0-\u1DFF\u1E00-\u1EFF\u1F00-\u1FFF\u2000-\u206F\u2070-\u209F\u20A0-\u20CF\u20D0-\u20FF\u2100-\u214F\u2150-\u218F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u2400-\u243F\u2440-\u245F\u2460-\u24FF\u2500-\u257F\u2580-\u259F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF\u27C0-\u27EF\u27F0-\u27FF\u2800-\u28FF\u2900-\u297F\u2980-\u29FF\u2A00-\u2AFF\u2B00-\u2BFF\u2C00-\u2C5F\u2C60-\u2C7F\u2C80-\u2CFF\u2D00-\u2D2F\u2D30-\u2D7F\u2D80-\u2DDF\u2DE0-\u2DFF\u2E00-\u2E7F\u2E80-\u2EFF\u2F00-\u2FDF\u2FE0-\u2FEF\u2FF0-\u2FFF\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u3100-\u312F\u3130-\u318F\u3190-\u319F\u31A0-\u31BF\u31C0-\u31EF\u31F0-\u31FF\u3200-\u32FF\u3300-\u33FF\u3400-\u4DBF\u4DC0-\u4DFF\u4E00-\u9FFF\uA000-\uA48F\uA490-\uA4CF\uA4D0-\uA4FF\uA500-\uA63F\uA640-\uA69F\uA6A0-\uA6FF\uA700-\uA71F\uA720-\uA7FF\uA800-\uA82F\uA830-\uA83F\uA840-\uA87F\uA880-\uA8DF\uA8E0-\uA8FF\uA900-\uA92F\uA930-\uA95F\uA960-\uA97F\uA980-\uA9DF\uA9E0-\uA9FF\uAA00-\uAA5F\uAA60-\uAA7F\uAA80-\uAADF\uAAE0-\uAAFF\uAB00-\uAB2F\uAB30-\uAB6F\uAB70-\uABBF\uABC0-\uABFF\uAC00-\uD7AF\uD7B0-\uD7FF\uD800-\uDB7F\uDB80-\uDBFF\uDC00-\uDFFF\uE000-\uF8FF\uF900-\uFAFF\uFB00-\uFB4F\uFB50-\uFDFF\uFE00-\uFE0F\uFE10-\uFE1F\uFE20-\uFE2F\uFE30-\uFE4F\uFE50-\uFE6F\uFE70-\uFEFF\uFF00-\uFFEF]', '', text)
        return text.strip()
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return list(self.language_map.keys())
    
    def _is_rtl_language(self, lang_code):
        """Check if language is RTL"""
        return lang_code in self.rtl_languages
    
    def _is_complex_script(self, lang_code):
        """Check if language uses complex script"""
        return lang_code in self.complex_script_languages
    
    def _chunk_text_smart(self, text, max_length=200, target_lang=None):
        """
        Smart text chunking that respects word boundaries in different scripts
        
        Args:
            text (str): Text to chunk
            max_length (int): Maximum length per chunk
            target_lang (str): Target language for script-aware chunking
            
        Returns:
            list: List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        # For complex scripts, use different chunking strategy
        if target_lang and self._is_complex_script(target_lang):
            return self._chunk_complex_script(text, max_length)
        
        # For RTL languages, be more careful with chunking
        if target_lang and self._is_rtl_language(target_lang):
            return self._chunk_rtl_text(text, max_length)
        
        # Default chunking for Latin scripts
        return self._chunk_text_default(text, max_length)
    
    def _chunk_complex_script(self, text, max_length):
        """Chunk text for complex scripts like Arabic, Hindi, Urdu"""
        chunks = []
        current_chunk = ""
        
        # Split by sentence endings common in these languages
        sentences = re.split(r'[۔؟!।॥|।?!]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max length, start new chunk
            if len(current_chunk) + len(sentence) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # If single sentence is too long, split by spaces but preserve word integrity
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 > max_length:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = word
                            else:
                                # If single word is too long, just add it
                                chunks.append(word)
                        else:
                            temp_chunk += " " + word if temp_chunk else word
                    if temp_chunk:
                        current_chunk = temp_chunk
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_rtl_text(self, text, max_length):
        """Chunk RTL text preserving reading direction"""
        chunks = []
        current_chunk = ""
        
        # Split by common RTL punctuation
        sentences = re.split(r'[۔؟!]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # For RTL, split by spaces but be careful with word boundaries
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 > max_length:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = word
                            else:
                                chunks.append(word)
                        else:
                            temp_chunk += " " + word if temp_chunk else word
                    if temp_chunk:
                        current_chunk = temp_chunk
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_text_default(self, text, max_length):
        """Default chunking for Latin scripts"""
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max length, start new chunk
            if len(current_chunk) + len(sentence) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # If single sentence is too long, split by words
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 > max_length:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = word
                            else:
                                # If single word is too long, just add it
                                chunks.append(word)
                        else:
                            temp_chunk += " " + word if temp_chunk else word
                    if temp_chunk:
                        current_chunk = temp_chunk
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _clean_translation_output(self, text, target_lang):
        """Clean translation output to remove mixed characters"""
        if not text:
            return text
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # For Urdu, Arabic, and other RTL languages
        if target_lang in ['ur', 'ar', 'fa', 'ps']:
            # Remove any Latin characters that might have leaked in
            # Keep only Arabic/Persian/Urdu script characters and basic punctuation
            text = re.sub(r'[a-zA-Z]', '', text)
            # Clean up extra spaces
            text = re.sub(r'\s+', ' ', text)
        
        # For Hindi and other Devanagari scripts
        elif target_lang in ['hi', 'mr', 'ne']:
            # Remove Latin characters
            text = re.sub(r'[a-zA-Z]', '', text)
            text = re.sub(r'\s+', ' ', text)
        
        # For other Indic languages
        elif target_lang in ['bn', 'gu', 'kn', 'ml', 'or', 'pa', 'si', 'ta', 'te']:
            # Remove Latin characters
            text = re.sub(r'[a-zA-Z]', '', text)
            text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def translate_text(self, text, source_lang="en", target_lang="en"):
        """
        Translate text from source language to target language
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code (auto-detect if None)
            target_lang (str): Target language code
            
        Returns:
            dict: Translation result with metadata
        """
        print(f"Translating from {source_lang} to {target_lang}: {text[:50]}...")  
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "Empty text provided"
                }
            
            # Auto-detect source language if not provided
            if source_lang is None:
                source_lang = self.detect_language(text)
            
            # Check if source and target are the same
            if source_lang == target_lang:
                return {
                    "success": True,
                    "original_text": text,
                    "translated_text": text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": 1.0,
                    "message": "Source and target languages are the same"
                }
            
            # Validate languages
            if source_lang not in self.language_map:
                return {
                    "success": False,
                    "error": f"Unsupported source language: {source_lang}"
                }
            
            if target_lang not in self.language_map:
                return {
                    "success": False,
                    "error": f"Unsupported target language: {target_lang}"
                }
            
            # Prepare translation
            logger.info(f"Translating from {source_lang} to {target_lang}")
            
            # Check if text is too long and needs chunking
            if len(text) > self.max_chunk_length:
                return self._translate_long_text(text, source_lang, target_lang)
            
            # For short texts, translate directly
            return self._translate_single_chunk(text, source_lang, target_lang)
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}"
            }
    
    def _translate_single_chunk(self, text, source_lang, target_lang):
        """Translate a single chunk of text"""
        try:
            # For mBART model, we need to set src_lang and tgt_lang
            if "mbart" in self.model_name.lower():
                # mBART uses specific language codes
                src_lang_code = self._get_mbart_lang_code(source_lang)
                tgt_lang_code = self._get_mbart_lang_code(target_lang)
                
                result = self.translator(
                    text,
                    src_lang=src_lang_code,
                    tgt_lang=tgt_lang_code,
                    max_length=512,  # Increased for better quality
                    num_beams=4,  # Increased for better quality
                    early_stopping=True,
                    do_sample=False,  # Deterministic output
                    temperature=1.0
                )
            else:
                # For other models
                result = self.translator(
                    text,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False
                )
            
            translated_text = result[0]['translation_text'] if isinstance(result, list) else result['translation_text']
            
            # Clean the translation output
            translated_text = self._clean_translation_output(translated_text, target_lang)
            
            return {
                "success": True,
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "source_language_name": self.language_map.get(source_lang, source_lang),
                "target_language_name": self.language_map.get(target_lang, target_lang),
                "confidence": 0.9,
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Single chunk translation error: {e}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}"
            }
    
    def _translate_long_text(self, text, source_lang, target_lang):
        """Translate long text by chunking"""
        try:
            # Split text into chunks using smart chunking
            chunks = self._chunk_text_smart(text, self.max_chunk_length, target_lang)
            logger.info(f"Splitting text into {len(chunks)} chunks")
            
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Translating chunk {i+1}/{len(chunks)}")
                
                # Translate each chunk
                result = self._translate_single_chunk(chunk, source_lang, target_lang)
                
                if result['success']:
                    translated_chunks.append(result['translated_text'])
                else:
                    logger.error(f"Failed to translate chunk {i+1}: {result['error']}")
                    # Use original chunk if translation fails
                    translated_chunks.append(chunk)
            
            # Combine translated chunks with appropriate separator
            separator = " " if not self._is_rtl_language(target_lang) else " "
            final_translation = separator.join(translated_chunks)
            
            # Final cleaning
            final_translation = self._clean_translation_output(final_translation, target_lang)
            
            return {
                "success": True,
                "original_text": text,
                "translated_text": final_translation,
                "source_language": source_lang,
                "target_language": target_lang,
                "source_language_name": self.language_map.get(source_lang, source_lang),
                "target_language_name": self.language_map.get(target_lang, target_lang),
                "confidence": 0.85,  # Slightly lower confidence for chunked translations
                "model_used": self.model_name,
                "chunks_processed": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Long text translation error: {e}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}"
            }
    
    def _get_mbart_lang_code(self, lang_code):
        """Convert language code to mBART format"""
        # Updated mBART language mappings with better coverage
        mbart_mappings = {
            'en': 'en_XX',
            'es': 'es_XX',
            'fr': 'fr_XX',
            'de': 'de_DE',
            'it': 'it_IT',
            'pt': 'pt_XX',
            'ru': 'ru_RU',
            'zh': 'zh_CN',
            'ja': 'ja_XX',
            'ko': 'ko_KR',
            'ar': 'ar_AR',
            'hi': 'hi_IN',
            'tr': 'tr_TR',
            'pl': 'pl_PL',
            'nl': 'nl_XX',
            'sv': 'sv_SE',
            'cs': 'cs_CZ',
            'ro': 'ro_RO',
            'fi': 'fi_FI',
            'he': 'he_IL',
            'th': 'th_TH',
            'vi': 'vi_VN',
            'id': 'id_ID',
            'ms': 'ms_MY',
            'bn': 'bn_IN',
            'gu': 'gu_IN',
            'kn': 'kn_IN',
            'ml': 'ml_IN',
            'mr': 'mr_IN',
            'ne': 'ne_NP',
            'pa': 'pa_IN',
            'si': 'si_LK',
            'ta': 'ta_IN',
            'te': 'te_IN',
            'ur': 'ur_PK',  # Fixed Urdu mapping
            'my': 'my_MM',
            'km': 'km_KH',
            'ka': 'ka_GE',
            'hy': 'hy_AM',
            'az': 'az_AZ',
            'kk': 'kk_KZ',
            'ky': 'ky_KG',
            'mn': 'mn_MN',
            'fa': 'fa_IR',  # Persian/Farsi
            'ps': 'ps_AF',  # Pashto
            'af': 'af_ZA',
            'tl': 'tl_XX',  # Filipino
            'sw': 'sw_KE'   # Swahili
        }
        
        return mbart_mappings.get(lang_code, 'en_XX')
    
    def batch_translate(self, texts, source_lang=None, target_lang="en"):
        """
        Translate multiple texts
        
        Args:
            texts (list): List of texts to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            list: List of translation results
        """
        results = []
        for i, text in enumerate(texts):
            logger.info(f"Translating batch item {i+1}/{len(texts)}")
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
        return results
    
    def get_translation_summary(self, result):
        """Get a summary of translation result"""
        if not result.get("success"):
            return f"Translation failed: {result.get('error', 'Unknown error')}"
        
        summary = f"""
        ✅ Translation successful!
        📝 Original ({result['source_language_name']}): {result['original_text'][:100]}...
        🔄 Translated ({result['target_language_name']}): {result['translated_text'][:100]}...
        🤖 Model: {result['model_used']}
        📊 Confidence: {result['confidence']:.1%}
        """
        
        if 'chunks_processed' in result:
            summary += f"\n🔧 Chunks processed: {result['chunks_processed']}"
        
        return summary
@session.bind(
    name="translation_agent",
    description="This agent translates the text from one language to the other language"
)
async def translation_agent(
    agent_context: GenAIContext,
    test_arg,
    source_lang, target_lang
):
    """This agent translates the text from one language to the other language"""
    translation=TranslationAgent().translate_text(test_arg, source_lang, target_lang)
    print(translation)
    agent_context.logger.info("Translation is: "+translation["translated_text"])

    return translation["translated_text"]


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
