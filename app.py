import csv
from pathlib import Path

import streamlit as st

CSV_PATH = Path(__file__).with_name("units.csv")


@st.cache_data
def laad_eenheden(pad: Path):
    with pad.open("r", encoding="utf-8-sig", newline="") as bestand:
        regels = list(csv.DictReader(bestand))

    eenheden = []
    for regel in regels:
        eenheden.append(
            {
                "grootheid": regel["grootheid"],
                "eenheid": regel["eenheid"],
                "symbool": regel["symbool"],
                "factor": float(regel["factor_naar_SI"]),
                "dimensie": (
                    int(regel["macht_massa"]),
                    int(regel["macht_lengte"]),
                    int(regel["macht_tijd"]),
                ),
                "afgeleid": regel["afgeleid"].lower() == "ja",
                "definitie_si": regel["definitie_SI"],
            }
        )
    return eenheden


def label(eenheid):
    return f'{eenheid["eenheid"]} ({eenheid["symbool"]})'


def zet_om(waarde, bron, doel):
    if bron["dimensie"] != doel["dimensie"]:
        raise ValueError("De eenheden hebben niet dezelfde fysische dimensie.")
    waarde_si = waarde * bron["factor"]
    return waarde_si / doel["factor"]


st.set_page_config(page_title="Eenheden omzetten", page_icon="📐")
st.title("Eenheden omzetten")
st.caption("Massa, tijd, lengte, oppervlakte, kracht en druk")

try:
    alle_eenheden = laad_eenheden(CSV_PATH)
except FileNotFoundError:
    st.error("Het bestand units.csv staat niet naast app.py.")
    st.stop()
except (KeyError, ValueError) as fout:
    st.error(f"De CSV-lijst heeft een ongeldige structuur: {fout}")
    st.stop()

grootheden = []
for eenheid in alle_eenheden:
    if eenheid["grootheid"] not in grootheden:
        grootheden.append(eenheid["grootheid"])

grootheid = st.selectbox("Grootheid", grootheden)
keuzes = [e for e in alle_eenheden if e["grootheid"] == grootheid]

kolom1, kolom2 = st.columns(2)
with kolom1:
    waarde = st.number_input("Waarde", value=1.0, format="%.10g")
    bron = st.selectbox("Van", keuzes, format_func=label)
with kolom2:
    st.write("")
    st.write("")
    doel = st.selectbox("Naar", keuzes, index=min(1, len(keuzes) - 1), format_func=label)

resultaat = zet_om(waarde, bron, doel)
st.success(f"{waarde:g} {bron['symbool']} = {resultaat:.10g} {doel['symbool']}")

with st.expander("Hoe werkt het systeem voor afgeleide eenheden?"):
    m, l, t = bron["dimensie"]
    st.write(
        "Elke eenheid krijgt drie machten: massa M, lengte L en tijd T. "
        "Een omzetting is alleen toegestaan als die drie machten gelijk zijn."
    )
    st.write(f"Dimensie van {grootheid}: M^{m} L^{l} T^{t}")
    st.write(f"SI-definitie: {bron['definitie_si']}")
    st.write(
        "Voorbeelden: oppervlakte is L^2, kracht is M L T^-2 en druk is M L^-1 T^-2."
    )
