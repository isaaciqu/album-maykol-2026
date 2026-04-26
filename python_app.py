import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, jsonify
import os
import json

app = Flask(__name__)

def obtener_datos():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # LÓGICA PASO B: Leer llave desde Nube o desde Archivo Local
        google_json = os.environ.get('GOOGLE_JSON')
        
        if google_json:
            # Si estamos en Render (Nube)
            creds_dict = json.loads(google_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Si estamos en tu PC (Local)
            creds = ServiceAccountCredentials.from_json_keyfile_name("llave_google1.json", scope)
            
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key("175LzyLlO9ZjZyp1rKkzltVfHLMaJX6uYzEsaVSpVrZc")
        hoja = spreadsheet.get_worksheet(0)
        matriz = hoja.get_all_values()
        
        datos = {"mundial": {}, "grupo_e": {}, "grupo_t": {}, "letras": {}}

        # Configuración de columnas (AK a AZ)
        config_cols = [
            {"col": 36, "inicio": 1, "fin": 99},
            {"col": 39, "inicio": 100, "fin": 199},
            {"col": 42, "inicio": 200, "fin": 299},
            {"col": 45, "inicio": 300, "fin": 399},
            {"col": 48, "inicio": 400, "fin": 499},
            {"col": 51, "inicio": 500, "fin": 584}
        ]

        for config in config_cols:
            c = config["col"]
            for fig in range(config["inicio"], config["fin"] + 1):
                try:
                    if fig in [100, 200, 300, 400, 500]:
                        valor = matriz[4][c].strip()
                    elif c == 51 and fig >= 580:
                        valor = matriz[84 + (fig - 580)][c].strip()
                    else:
                        offset = (fig % 100) - 1 if fig % 100 != 0 else 0
                        valor = matriz[5 + offset][c].strip()
                    datos["mundial"][str(fig)] = valor
                except: datos["mundial"][str(fig)] = "---"

        # Grupos E y T
        for f in range(4, 71):
            try:
                id_e = matriz[f][57].strip()
                if id_e: datos["grupo_e"][id_e] = matriz[f][58].strip()
            except: pass
            try:
                id_t = matriz[f][60].strip()
                if id_t: datos["grupo_t"][id_t] = matriz[f][61].strip()
            except: pass
        
        # Grupo Letras
        letras_ids = ["A", "B", "C", "D", "G", "E", "F"]
        for i, letra in enumerate(letras_ids):
            try:
                datos["letras"][letra] = matriz[4 + i][53].strip()
            except: pass

        return datos
    except Exception as e:
        print(f"Error V4.5: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/figuritas')
def api():
    d = obtener_datos()
    return jsonify(d) if d else jsonify({"error": "fail"})

if __name__ == '__main__':
    # Puerto dinámico para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)