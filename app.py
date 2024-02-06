import streamlit as st
from streamlit_option_menu import option_menu

from Youtube_Transcript.main import StreamlitApp
from streamlit_login_auth_ui_with_firebase.utils import initialize_firebase
from streamlit_login_auth_ui_with_firebase.widgets import __login__

hide = """
   <style>
       #GithubIcon {visibility: hidden;}
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
   </style>
   """
st.markdown(hide, unsafe_allow_html=True)
initialize_firebase("https://transcript-59edb-default-rtdb.firebaseio.com/","auth.json")
__login__obj = __login__(auth_token = "pk_prod_D73N19AVYQ4X7RHWZ477B0Y5SRWM",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'تسجيل الخروج', hide_menu_bool = False,
                    hide_footer_bool = False,)

LOGGED_IN= __login__obj.build_login_ui()
email= __login__obj.get_email()


if LOGGED_IN == True:
    app = StreamlitApp()
    app.run(email)
