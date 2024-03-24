import base64
from source.utils import genformer_runner
import streamlit as st
from PIL import Image
import pandas as pd

def main():
    st.set_page_config(layout="wide")
    st.header("Rapid Data Extraction Using GenAI", divider='rainbow')

    c1, c2, c3 = st.columns((2, 6, 5))

    with c1:
        try:
            uploaded_file = st.sidebar.file_uploader("Load File", type=["pdf", "png"])
            filename = uploaded_file.name
        except:
            print("nothing")
    with c1:
        try:
            if uploaded_file.type == 'application/pdf':
                base64_pdf = base64.b64encode(uploaded_file.read()).decode("utf-8")
                pdf_display = (
                    f'<embed src="data:application/pdf;base64,{base64_pdf}" '
                    'width="650" height="850" type="application/pdf"></embed>'
                )
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                image = Image.open(uploaded_file)
                c1.image(image, width=700)

            m = st.markdown(""" <style> div.stButton > button:first-child { background-color: rgb(114, 172, 114);border: none;
                        color: white;
                        padding: 16px 16px;
                        text-align: left;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 300px; } </style>""", unsafe_allow_html=True)
            process_button = st.button("Process")
        except:
            print("nothing")
        with c3:
            try:
                if st.columns(3)[1].process_button:
                    if process_button:
                        with c3:
                            output = genformer_runner.genformer_runner(filename)
                            output.index = output.index + 1
                            th_props = [
                                ('font-size', '16px'),
                                ('text-align', 'center'),
                                ('font-weight', 'bold'),
                                ('color', '#6d6d6d'),
                                ('background-color', '#f7ffff')
                            ]

                            td_props = [
                                ('font-size', '16px')
                            ]

                            styles = [
                                dict(selector="th", props=th_props),
                                dict(selector="td", props=td_props)
                            ]
                            df2 = output.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)
                            c3.table(df2)
            except:
                print("nothing")


if __name__ == "__main__":
    main()
