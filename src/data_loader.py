
import pandas as pd
import io, os
from dataclasses import dataclass

@dataclass(frozen=True)
class Columns:
    GRE: str = "GRE"
    MUNICIPIO: str = "MUNICIPIO"
    ESCOLA: str = "ESCOLA"
    CODIGOESCOLA: str = "CODIGOESCOLA"
    DATAS: str = "DATAS"

def save_uploaded_file_and_get_paths(uploaded_file, target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    file_name = uploaded_file.name
    save_path = os.path.join(target_dir, file_name)
    # salvar bytes
    uploaded_file.seek(0)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    return save_path, target_dir

def load_consolidacao(path_or_file) -> pd.DataFrame:
    # Leitura com valores salvos (data_only=True) para refletir o que está no arquivo
    # Como estamos lendo com pandas, asseguramos dtype=str para evitar problemas
    df = pd.read_excel(path_or_file, sheet_name="Consolidação", dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]

    # Mapeamento conforme a estrutura identificada:
    # A: REGIONAL -> GRE
    # B: MUNICÍPIO -> MUNICIPIO
    # D: INEP -> CODIGOESCOLA
    # E: ESCOLA -> ESCOLA
    # F: DATAS -> DATAS
    cols = df.columns.tolist()
    col_mapping = {
        cols[0]: Columns.GRE,
        cols[1]: Columns.MUNICIPIO,
        cols[3]: Columns.CODIGOESCOLA,
        cols[4]: Columns.ESCOLA,
        cols[5]: Columns.DATAS
    }
    df = df.rename(columns=col_mapping)

    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()

    # Indicador de data (qualquer valor não vazio e != "#N/D" conta como "com data")
    def has_date(v):
        v = str(v).strip().upper()
        return 0 if v in ["", "#N/D", "NAN", "NONE"] else 1

    df["HAS_DATE"] = df[Columns.DATAS].apply(has_date)
    return df
