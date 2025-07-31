import streamlit as st
import os
from dotenv import load_dotenv
from modules.generator_core import generate_docx_for_structure
from main import document_structure, document_structure_bab3, document_structure_bab4

load_dotenv()

st.set_page_config(
    page_title="Company Profile Generator",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color:#4B8BBE;'>📄 Company Profile Generator</h1>
        <p style='color:gray;'>Buat dokumen BAB II, III, IV profil perusahaan secara otomatis dengan AI dan riset online.</p>
        <hr style='border: 1px solid #ddd;'/>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("📂 Navigasi", [
    "Buat Dokumen Bab II",
    "Buat Dokumen Bab III",
    "Buat Dokumen Bab IV",
    "Tentang Aplikasi"
])

model_options = [
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash-latest",
    "models/gemini-2.5-pro",
    "models/gemini-2.5-flash"
]

def render_form(judul_bab, structure, filename_prefix):
    st.subheader(f"🧾 Formulir Input {judul_bab}")
    with st.form(f"form_input_{judul_bab.lower().replace(' ', '_')}"):
        company_name = st.text_input("Masukkan Nama Perusahaan", placeholder="Contoh: PT Pelabuhan Indonesia (Persero)")
        selected_model = st.selectbox("Model AI", model_options, index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
        depth = st.slider("Kedalaman Riset (Depth)", 1, 5, 2, 1)
        breadth = st.slider("Lebar Riset (Breadth)", 1, 10, 3, 1)
        submitted = st.form_submit_button(f"🚀 Buat Dokumen {judul_bab}")

    if submitted and company_name.strip():
        with st.spinner(f"Sedang membuat dokumen {judul_bab}..."):
            try:
                file_path, tokens_in, tokens_out = generate_docx_for_structure(
                    company_name=company_name.strip(),
                    document_structure=structure,
                    doc_title=judul_bab,
                    filename_prefix=judul_bab.replace(" ", "_"),
                    temperature=temperature,
                    model_name=selected_model,
                    depth=depth,
                    breadth=breadth
                )
                with open(file_path, "rb") as f:
                    st.success(f"✅ Dokumen {judul_bab} berhasil dibuat!")
                    st.download_button("📥 Download DOCX", f, file_name=os.path.basename(file_path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                st.markdown(f"🔢 **Token Input**: `{tokens_in}`")
                st.markdown(f"🧾 **Token Output**: `{tokens_out}`")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
    elif submitted:
        st.warning("⚠️ Nama perusahaan tidak boleh kosong.")

if menu == "Buat Dokumen Bab II":
    render_form("Bab II PENDAHULUAN", document_structure, "Bab_II_Profil")
elif menu == "Buat Dokumen Bab III":
    render_form("Bab III KINERJA PERUSAHAAN", document_structure_bab3, "Bab_III_Kinerja")
elif menu == "Buat Dokumen Bab IV":
    render_form("Bab IV ANALISIS POSISI PERUSAHAAN", document_structure_bab4, "Bab_IV_Analisis")
elif menu == "Tentang Aplikasi":
    st.subheader("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini membantu menyusun dokumen Bab II, III, dan IV profil perusahaan secara otomatis.

    ✅ Fitur:
    - Riset otomatis berbasis web (Firecrawl)
    - Integrasi dengan Gemini API
    - Output file .docx siap edit
    - Kendali temperature, depth, breadth
    - Setiap sub-bab mencantumkan sumber referensinya
    """)
