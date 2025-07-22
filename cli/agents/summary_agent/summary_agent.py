import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from transformers import pipeline, MBartForConditionalGeneration, MBart50Tokenizer, BartTokenizer
from langdetect import detect
import torch
import logging

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MzZhY2E1NC1kZmM5LTQzNWMtOTIyNC01NGRkNmRkZTRjNzEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjRhNmU2MzRkLWFmNGQtNDUwNy1hY2NmLWRjYjcxYzU4ZGJlMCJ9.Rf6ehWL1Mswx_Oi-wuDbAZ5LGuOU8lkF-lqQMKlTtrw" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

class SummarizeAgent:
    def __init__(self, model_name="facebook/mbart-large-50-one-to-many-mmt", use_cuda=True):
        """
        Initialize the SummarizeAgent with a multilingual BART model (mBART).
        
        :param model_name: Pretrained multilingual model name from HuggingFace Hub.
        :param use_cuda: Boolean to enable GPU acceleration.
        """
        # self.model_name = model_name
        self.use_cuda = use_cuda
        self.device = 0 if torch.cuda.is_available() and use_cuda else -1  # Set device for GPU/CPU
        self.model_name = "facebook/bart-large-cnn"
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.summarizer = pipeline("summarization", model=self.model_name, tokenizer=self.tokenizer, device=self.device)

        self.max_input_length = 1024  # Max length of input the model can handle

    def summarize(self, input_text: str, min_length=50, max_length=100, chunk_size=512) -> str:
        """
        Summarizes the input text with refined chunking, error handling, and performance optimizations.
        
        :param input_text: Text to summarize.
        :param min_length: Minimum number of words in summary.
        :param max_length: Maximum number of words in summary.
        :param chunk_size: Size of chunks before passing into the model.
        :return: The summary of the input text.
        """
        if not input_text.strip():
            logging.error("Empty text provided for summarization.")
            return "No input text provided to summarize."
        
        # Detect the language of the input text
        language = self._detect_language(input_text)
        if language not in ['en', 'fr', 'ar', 'de']:  # Support for English, French, Arabic, and German
            logging.warning(f"Unsupported language detected: {language}. Defaulting to English.")
            language = 'en'
        
        # Preprocess the input text
        input_text = self._preprocess_text(input_text)

        # Chunk the input text if it's too long
        input_chunks = self._chunk_text(input_text, self.max_input_length)

        summary = []
        for chunk in input_chunks:
            try:
                chunk_summary = self.summarizer(chunk, min_length=min_length, max_length=max_length, do_sample=False)
                summary.append(chunk_summary[0]['summary_text'])
            except Exception as e:
                logging.error(f"Error summarizing chunk: {str(e)}")
                summary.append("Summary unavailable due to processing error.")
        
        return ' '.join(summary)

    def _chunk_text(self, text: str, max_length: int) -> list:
        """
        Refined text chunking based on sentence breaks to ensure coherent chunking.
        
        :param text: The full input text to chunk.
        :param max_length: Maximum token length for each chunk.
        :return: A list of chunks.
        """
        if len(text.split()) <= max_length:
            return [text]
        
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= max_length:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                chunks.append('. '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append('. '.join(current_chunk))
        
        return chunks

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocesses the input text to make it cleaner and more effective for summarization.
        
        :param text: The input text to preprocess.
        :return: Preprocessed text.
        """
        # Basic text cleanup (e.g., removing extra spaces, unwanted characters)
        text = " ".join(text.split())  # Remove extra whitespace
        # Add more preprocessing steps here (like removing headers, footers, etc. if required)
        return text

    def _detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        :param text: The input text to detect language for.
        :return: Detected language code.
        """
        try:
            lang = detect(text)
            return lang
        except Exception as e:
            logging.error(f"Error detecting language: {str(e)}")
            return 'en'  # Default to English if detection fails

@session.bind(
    name="summary_agent",
    description="This agent will take text and summarize it to a shorter version"
)
async def summary_agent(
    agent_context: GenAIContext,
    test_arg 
):
    # Create an instance of SummarizeAgent
    agent_context.logger.info("Summarization has startes now")
    summarize_agent = SummarizeAgent()
    summary = summarize_agent.summarize(test_arg)
    agent_context.logger.info("Summary is "+ summary)
    print("Summary:")
    print(summary)

    """This agent will provide the summary of input text"""
    return summary


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())