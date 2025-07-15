from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os

@dataclass
class Disciplina:
    id: str
    nome: str
    curso: str
    ch_prevista: float = 0.0
    alunos_previstos: int = 0
    ch_por_aluno: float = 0.0  # Carga horária de preceptoria por aluno
    
@dataclass
class DadosReaisCampus:
    disciplina_id: str
    alunos_reais: int = 0
    ch_real_total: float = 0.0
    observacoes: str = ""

@dataclass
class Campus:
    id: str
    nome: str
    disciplinas: List[str] = field(default_factory=list)
    dados_reais: Dict[str, DadosReaisCampus] = field(default_factory=dict)

@dataclass
class CalculoResultado:
    disciplina_id: str
    disciplina_nome: str
    curso: str
    campus: str
    ch_prevista: float
    ch_real: float
    diferenca_ch: float
    alunos_previstos: int
    alunos_reais: int
    diferenca_alunos: int
    eficiencia: float  # CH Real / CH Prevista
    status: str  # "Excesso", "Falta", "Adequado"

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.disciplinas_file = os.path.join(data_dir, "disciplinas.json")
        self.campus_file = os.path.join(data_dir, "campus.json")
        
    def save_disciplinas(self, disciplinas: List[Disciplina]):
        data = [
            {
                "id": d.id,
                "nome": d.nome,
                "curso": d.curso,
                "ch_prevista": d.ch_prevista,
                "alunos_previstos": d.alunos_previstos,
                "ch_por_aluno": d.ch_por_aluno
            }
            for d in disciplinas
        ]
        with open(self.disciplinas_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_disciplinas(self) -> List[Disciplina]:
        if not os.path.exists(self.disciplinas_file):
            return []
        
        with open(self.disciplinas_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [
            Disciplina(
                id=item["id"],
                nome=item["nome"],
                curso=item["curso"],
                ch_prevista=item.get("ch_prevista", 0.0),
                alunos_previstos=item.get("alunos_previstos", 0),
                ch_por_aluno=item.get("ch_por_aluno", 0.0)
            )
            for item in data
        ]
    
    def save_campus(self, campus_list: List[Campus]):
        data = []
        for campus in campus_list:
            campus_data = {
                "id": campus.id,
                "nome": campus.nome,
                "disciplinas": campus.disciplinas,
                "dados_reais": {}
            }
            
            for disc_id, dados in campus.dados_reais.items():
                campus_data["dados_reais"][disc_id] = {
                    "disciplina_id": dados.disciplina_id,
                    "alunos_reais": dados.alunos_reais,
                    "ch_real_total": dados.ch_real_total,
                    "observacoes": dados.observacoes
                }
            
            data.append(campus_data)
        
        with open(self.campus_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_campus(self) -> List[Campus]:
        if not os.path.exists(self.campus_file):
            return []
        
        with open(self.campus_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        campus_list = []
        for item in data:
            campus = Campus(
                id=item["id"],
                nome=item["nome"],
                disciplinas=item.get("disciplinas", [])
            )
            
            for disc_id, dados_dict in item.get("dados_reais", {}).items():
                campus.dados_reais[disc_id] = DadosReaisCampus(
                    disciplina_id=dados_dict["disciplina_id"],
                    alunos_reais=dados_dict.get("alunos_reais", 0),
                    ch_real_total=dados_dict.get("ch_real_total", 0.0),
                    observacoes=dados_dict.get("observacoes", "")
                )
            
            campus_list.append(campus)
        
        return campus_list