import streamlit as st
from firebase_admin import db
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import HuggingFaceHub
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

from Youtube_Transcript.utils import Translator, TextProcessor, YouTubeTranscript


# Import your TextProcessor, Translator, YouTubeTranscript classes
# from text_processing import TextProcessor, Translator, YouTubeTranscript
def inject_custom_css():
    custom_css = """
    <style>
        .css-r421ms.e10yg2by1 {
            border: 1px solid rgba(7, 141, 239, 0.83);
            border-radius: 1.5rem;
            padding: calc(1em - 1px);
            background-color: azure;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

class StreamlitApp:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.huggingfacehub_api_token = "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"
        self.repo_id = "tiiuae/falcon-7b-instruct"
        self.falcon_llm = HuggingFaceHub(
            huggingfacehub_api_token=self.huggingfacehub_api_token,
            repo_id=self.repo_id, model_kwargs={"temperature": 0.1, "max_new_tokens": 1000}
        )


    @staticmethod
    def increment_numclick(user_id):
        user_ref = db.reference(f'/users/{user_id}')
        user_data = user_ref.get()

        if user_data and 'numclick' in user_data:
            current_numclick = int(user_data['numclick']) if user_data['numclick'].isdigit() else 0
            user_ref.update({"numclick": str(current_numclick + 1)})
        else:
            print("User not found or numclick field does not exist.")

    @staticmethod
    def get_user_id_by_attribute(attribute, value):
        users_ref = db.reference('users')
        users = users_ref.get()

        for user_id, user_data in users.items():
            if user_data.get(attribute) == value:
                return user_id
        return None
    def run(self,email):
        st.title("YouTube Transcript Summarizer and Translator")
        # inject_custom_css()
        with st.form("transcript_form"):
            video_url = st.text_input("Enter YouTube URL", "")
            target_language = st.selectbox("Select Language", ["English", "Arabic"])
            submit_button = st.form_submit_button("Get Transcript")

        if submit_button:
            with st.spinner('Processing...'):
                try:
                    user_id = self.get_user_id_by_attribute('email', email)
                    self.increment_numclick(user_id)
                    video_id = YouTubeTranscript.get_youtube_id(video_url)
                    if video_id:
                        srt_text = YouTubeTranscript.save_transcript_as_srt(video_id)
                        loader = YoutubeLoader.from_youtube_url(video_url)
                        transcript = loader.load()
                        full_transcript = ' '.join([t.page_content for t in transcript])
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
                        docs = text_splitter.split_documents(transcript)

                        chain = load_summarize_chain(self.falcon_llm, chain_type="map_reduce", verbose=True)
                        output_summary = chain.run(docs)
                        output = TextProcessor.remove_duplicate_sentences(
                            TextProcessor.remove_similar_sentences(output_summary))

                        if target_language == "English":
                            st.subheader("Summary of Video")
                            st.text_area("Summary", output, height=150)
                            st.download_button(
                                label="Download English Transcript with .srt",
                                data=srt_text,
                                file_name="transcript_english.srt",
                                mime="text/plain"
                            )

                        elif target_language == "Arabic":
                            arabic_output = Translator.translate_arabic_to_english(output)
                            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                            base_obj = transcripts.find_transcript(['en'])
                            txt_formatter = TextFormatter()
                            srt_formatter = SRTFormatter()
                            if base_obj.is_translatable:
                                wanted_tran = base_obj.translate('ar').fetch()
                            else:
                                st.error("Cannot translate transcript to Arabic")
                                return
                            full_transcript = txt_formatter.format_transcript(wanted_tran)
                            wanted_srt = srt_formatter.format_transcript(wanted_tran)

                            st.subheader("Arabic Summary of Video")
                            st.text_area("Summary", arabic_output, height=150)
                            st.download_button(
                                label="Download Arabic Transcript with .srt",
                                data=wanted_srt,
                                file_name="transcript_arabic.srt",
                                mime="text/plain"
                            )

                        st.download_button(
                            label="Download Transcript",
                            data=full_transcript,
                            file_name="transcript.txt",
                            mime="text/plain"
                        )

                    else:
                        st.error("Invalid YouTube URL")
                except Exception as e:
                    st.error(f"An error occurred: {e}")


