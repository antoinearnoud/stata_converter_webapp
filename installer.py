import os
with open(os.path.join('/Users/aarnoud/Dropbox/Research_2020/stata_converter_webapp','Procfile'), "w") as file1:
    toFile = 'web: sh setup.sh && streamlit run converter.py'
    file1.write(toFile)
