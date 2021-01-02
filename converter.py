# Note: run with pythonw cameleon.py
# to run this program
# activate environment: conda activate insight
# run: streamlit run shibah.py

import streamlit as st
import pandas as pd
import os
import base64
import datetime

st.title("Stata Converter WebApp")
st.warning("Application created by antoine.arnoud@pm.com to convert Stata files into previous versions.")
st.markdown('Desktop application available for <a href="https://github.com/antoinearnoud/stata_converter"> Mac </a>', unsafe_allow_html=True)

@st.cache(suppress_st_warning=True, show_spinner=False)
def load_stata(filename):
    df = pd.read_stata(filename)
    return df


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def delete_old_files():
    files = os.listdir("temp/")
    #st.write(files)
    if (files is None) or (files == []):
        #st.write("files is none")
        return
    for file in files:
        if file == "readme.md":
            continue
        curpath = os.path.join("temp", file)
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
        #st.write(file + " was modified at " + str(file_modified))
        if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
            print("deleting: " + file)
            os.remove(curpath)


delete_old_files()
file_uploaded = st.file_uploader("Choose a Stata file to convert", type=["dta"])
if not (file_uploaded is None):
    df = load_stata(file_uploaded)
    file_details = {"FileName":file_uploaded.name,"FileType":file_uploaded.type,"FileSize":file_uploaded.size}
    filename = file_details["FileName"]
    version = st.radio("Convert file to Stata version", ["Stata 10", "Stata 13", "Stata 14"])
    base_filename = filename.replace(".dta","")
    if version == "Stata 10": extension, ver = "_v10", 114
    if version == "Stata 13": extension, ver = "_v13", 117
    if version == "Stata 14": extension, ver = "_v14", 118
    newname = base_filename + extension + ".dta"
    if st.button('Convert file'):
        df.to_stata(os.path.join('temp', newname), version = ver, write_index = False)
    #st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    #f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'
        st.info("Download converted file below")
        st.markdown(get_binary_file_downloader_html(os.path.join('temp', newname), file_label='File'), unsafe_allow_html=True)
