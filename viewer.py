import streamlit as st
import pandas as pd
import pickle
import sncosmo
from astropy.table import Table
from utils import get_saved_notes, save_note_to_file


dust = sncosmo.CCM89Dust()
st.set_page_config(layout="wide")
st.title("Lasair SN candidates")


@st.cache_data
def load_data():
    with open('outputs/processed_data.pkl', 'rb') as f:
        return pickle.load(f)

data_dict = load_data()
target_id = st.sidebar.selectbox("Select Candidate", list(data_dict.keys()))

obj_data = data_dict[target_id]
lc_tab = Table.from_pandas(obj_data['lc_table'])
model_params = obj_data['model_params']
fit_errors = obj_data['fit_params'].get('errors')

model = sncosmo.Model(source='salt2-extended', effects=[dust], effect_names=['MW'], effect_frames=['obs'])
model.set(**model_params)


col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"SN candidate: {target_id}")
    st.write(f'https://lasair-ztf.lsst.ac.uk/objects/{target_id}')

    st.write("*ZTF Metadata*")
    metadata_df = pd.DataFrame([obj_data['metadata']]).T
    metadata_df.columns = ["Value"]
    metadata_df['Value'] = metadata_df['Value'].astype(str)

    st.table(metadata_df)

    st.write("*SALT fit Results:*")
    st.json(obj_data['fit_params'])
    fig = sncosmo.plot_lc(lc_tab, model=model, errors=fit_errors)
    st.pyplot(fig)
    
    

with col2:
    st.subheader("Host Galaxy Context")
    ra, dec = obj_data['metadata']['ramean'], obj_data['metadata']['decmean']
    url = f"https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&layer=ls-dr10&pixscale=0.262"
    st.image(url, width = 'stretch')
    
    st.subheader("Raw Light Curve Data")
    st.dataframe(obj_data['lc_table'], height=300)


st.sidebar.markdown("---")
st.sidebar.subheader(f"Notes for {target_id}")


all_notes = get_saved_notes()
current_note_content = all_notes.get(target_id, "")

user_note = st.sidebar.text_area(
    "Comments",
    value=current_note_content,
    key=f"note_input_{target_id}",
    height=150
)

if st.sidebar.button("Save notes"):
    save_note_to_file(target_id, user_note)
    st.sidebar.success(f"Successfully saved notes for {target_id}")

