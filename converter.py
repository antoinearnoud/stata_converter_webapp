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
st.info("Application by antoine.arnoud@gmail.com to convert Stata files into previous Stata versions.")
#st.markdown('Desktop application available for <a href="https://github.com/antoinearnoud/stata_converter"> Mac </a>', unsafe_allow_html=True)
st.markdown('Desktop application available for <a href="https://www.dropbox.com/sh/uv3g73e8hjltg84/AABJx5xFthkrtNbi2TGyRw9Ba?dl=0"> Mac </a>', unsafe_allow_html=True)

text_contents = '''This is some text'''
st.download_button("Download the file", text_contents)

#st.sidebar.info('Created by antoine.arnoud@gmail.com')
#st.sidebar.warning('Report errors')

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
        if datetime.datetime.now() - file_modified > datetime.timedelta(minutes = 20): #(hours=1):
            print("deleting: " + file)
            os.remove(curpath)

def record_file_name(filename, size, version):
    now = datetime.datetime.now().isoformat()
    filepath = 'filenames.csv'
    if os.path.exists(filepath):
        openmode = 'a'
    else:
        openmode = 'w'
    with open(filepath, mode = openmode) as recordfile:
        recordfile.write(filename +',' + str(size) + ',' + version + ',' + now)
        recordfile.write('\n')


# delete files in /temp/ older than 1 hour
delete_old_files()
# upload file to convert
file_uploaded = st.file_uploader("Choose a Stata file to convert (files are deleted from the server after 20 minutes)", type=["dta"], accept_multiple_files = False)
if not (file_uploaded is None):
    file_details = {"FileName":file_uploaded.name,"FileType":file_uploaded.type,"FileSize":file_uploaded.size}
    filename = file_details["FileName"]
    size = file_details['FileSize']
    if size > 40000000:
        st.warning("File too big: web app limited to files under 40MB. Try the desktop application.")
    else:
        version = st.radio("Convert file to Stata version", ["Stata 10", "Stata 13", "Stata 14"])
        base_filename = filename.replace(".dta","")
        if version == "Stata 10": extension, ver = "_v10", 114
        if version == "Stata 13": extension, ver = "_v13", 117
        if version == "Stata 14": extension, ver = "_v14", 118
        newname = base_filename + extension + ".dta"
        if st.button('Convert file'):
            record_file_name(filename, size, version)
            with st.spinner('Conversion in progress. Be patient...'):
                df = load_stata(file_uploaded)
                if os.path.exists(os.path.join('temp', newname)): #add an extension if the file already exists (because it might be the file of somebody else; so shouldn't download it)
                    newname = base_filename + '_' + datetime.datetime.now().strftime("%H%M%S")  + extension + ".dta"
                df.to_stata(os.path.join('temp', newname), version = ver, write_index = False)
            #st.markdown(get_table_download_link(df), unsafe_allow_html=True)
            #f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'
            #st.warning("Download converted file below")
            st.markdown(get_binary_file_downloader_html(os.path.join('temp', newname), file_label='converted stata file: ' + newname), unsafe_allow_html=True)
