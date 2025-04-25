import traceback
import os
import shutil

os.makedirs(".videos", exist_ok=True)
os.makedirs(".temp", exist_ok=True)

try:
    import streamlit as st

    st.set_page_config(layout="wide")

    from app.show_results import show_results

    pages = {
        "New Process" : [
            st.Page("app/process_video.py", title="Novo Processamento de Video", icon="📹", url_path="new", default=True),
        ],
        "Result Example" : [
            st.Page(lambda : show_results("", path="example"), title="Exemplo", icon="📊", url_path=f"result_example")
        ], 
        "Results" : [
            st.Page(lambda : show_results(entry.name), title=entry.name, icon="📊", url_path=f"result_{entry.name}")
            for entry in os.scandir(".videos") if entry.is_dir()
        ],

    }
    
    pg = st.navigation(pages)
    pg.run()

except Exception as e:
    st.error(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    shutil.rmtree(".temp")
    os.makedirs(".temp", exist_ok=True)