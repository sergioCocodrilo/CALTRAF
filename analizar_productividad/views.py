from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
from django.core.files.storage import default_storage
# export page as html text
from django.template.loader import render_to_string

import os

def index(request):
    uploaded_files = sorted([f for f in os.listdir() if f.endswith(".xls")])
    caltraf_files = list_files("caltraf", uploaded_files)
    cms, paso, bloi, bloe, b_data = caltraf(caltraf_files)
    cms_short = [(index, cm[3:]) for index,cm in cms]
    context = {
            'cms': cms,
            'cms_short': cms_short,
            'paso': paso,
            'bloi': bloi,
            'bloe': bloe,
            'b_data': b_data,
            'caltraf_files': caltraf_files,
            }
    content = render_to_string("analizar_productividad/index_2.html", context)
    with open('static_html/caltraf.html', 'w') as static_file:
        static_file.write(content)
    return render(request, "analizar_productividad/index_2.html", context)

def upload_file(request):
    data = {'msg':''}
    if request.method == "GET":
        return render(request, 'analizar_productividad/upload_form.html', data)
    try:
        uploaded_file = request.FILES['file']
        if uploaded_file.name.endswith(".xls"):
            file_name = default_storage.save(uploaded_file.name, uploaded_file)
            return index(request)
    except Exception as e:
        print(e)
    data = {'msg': 'No se cargó ningún archivo.'}
    return render(request, 'analizar_productividad/upload_form.html', data)

def main_processing(request):
    print("procesando...")
    caltraf()        # all data frames

#-------------------- reading files
def list_files(string_filter, uploaded_files):
    files = [f for f in uploaded_files if f.lower().startswith(string_filter)]
    return files 

#-------------------- processing
import pandas as pd

def caltraf(caltraf_files):
    # build data frame
    dfs = []
    for f in caltraf_files:
        dfs.append(pd.read_excel(f, sheet_name="Datos"))
    df = pd.concat(dfs)
        
    # clean missing data
    df.dropna(inplace=True)

    cms = [(index, cm) for index, cm in enumerate(sorted(df["CENTRO DE MANTENIMIENTO"].unique()))]
    buildings = df.groupby(["CENTRO DE MANTENIMIENTO", "CLLI_REAL", "EDIFICIO"])
    paso_dict = {}
    bloi_dict = {}
    bloe_dict = {}
    buildings_data = {}
    errors_cols = ["D.- INC", "E.- TNP", "Bloi", "Bloe", "FTS", "FTE", "OPR", "Falla Tecnica"]
    for k, gr in buildings:
        b_data = {}
        # porcentaje de paso
        percentage = gr["Paso"] / gr["F.- Intentos"]
        b_data['Paso'] = per_to_str(percentage)

        # errores
        total_error_por_meses = 1 + gr[["D.- INC", "E.- TNP", "Bloi", "Bloe", "FTS", "FTE", "OPR", "Falla Tecnica"]].sum(axis=1)
        cols_names = ["INC", "TNP", "Bloi", "Bloe", "FTS", "FTE", "OPR", "Falla_Tecnica"]
        for i, col in enumerate(errors_cols):
            percentage = gr[col] / total_error_por_meses
            b_data[cols_names[i]] = per_to_str(percentage)
        buildings_data[k] = b_data

    return cms, paso_dict, bloi_dict, bloe_dict, buildings_data

def per_to_str(percentage):
    per_str = []
    for p in percentage:
        buff_size = 30
        a = int(round(p * buff_size, ndigits=0))
        b = buff_size - a
        per_str.append('▓' * a + '░' * b + '  ' + str(round(p * 100, ndigits=2)) + '%')
    return per_str
