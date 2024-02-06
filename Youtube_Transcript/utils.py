# text_processing.py
import difflib
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from deep_translator import GoogleTranslator


class TextProcessor:
    @staticmethod
    def remove_similar_sentences(text, similarity_threshold=0.8):
        sentences = text.split('. ')
        filtered_sentences = []
        for sentence in sentences:
            if not any(difflib.SequenceMatcher(None, sentence, s).ratio() > similarity_threshold for s in filtered_sentences):
                filtered_sentences.append(sentence)
        return '. '.join(filtered_sentences)

    @staticmethod
    def remove_duplicate_sentences(text):
        normalized_text = text.replace('\n', ' ').replace('-', '').strip()
        sentences = normalized_text.split('. ')
        unique_sentences = set()
        result = []
        for sentence in sentences:
            normalized_sentence = sentence.lower().strip()
            if normalized_sentence not in unique_sentences:
                unique_sentences.add(normalized_sentence)
                result.append(sentence.strip())
        return '. '.join(result)

class Translator:
    @staticmethod
    def translate_text(text, source_language, target_language):
        translator = GoogleTranslator(source=source_language, target=target_language)
        max_chunk_size = 4995
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return ''.join(translated_chunks)

    @staticmethod
    def translate_arabic_to_english(text):
        return Translator.translate_text(text, 'english', 'arabic')

    @staticmethod
    def translate_srt(srt_content, source_language, target_language, additional_line):
        translated_lines = []
        text_block = ''
        lines = srt_content.split('\n')
        for line in lines:
            if line.strip().isnumeric():
                if text_block:
                    translated_lines.append(Translator.translate_text(text_block, source_language, target_language))
                    text_block = ''
                translated_lines.append(additional_line + '\n')
                translated_lines.append(line + '\n')
            elif '-->' in line:
                translated_lines.append(line + '\n')
            else:
                text_block += line.strip() + ' '
        if text_block:
            translated_lines.append(Translator.translate_text(text_block, source_language, target_language) + '\n')
        return ''.join(translated_lines)

class YouTubeTranscript:
    @staticmethod
    def save_transcript_as_srt(video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = SRTFormatter()
            srt_transcript = formatter.format_transcript(transcript)
            return srt_transcript
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def get_youtube_id(url):
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?\s"]{11})'
        )
        youtube_regex_match = re.match(youtube_regex, url)
        if youtube_regex_match:
            return youtube_regex_match.group(6)
        return None
