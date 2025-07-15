#!/usr/bin/env python3
"""
Script para popular dados de exemplo na calculadora de preceptores.
Execute este script para criar dados de teste e demonstração.
"""

import uuid
from models import Disciplina, Campus, DataManager, DadosReaisCampus

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstração do sistema"""
    
    data_manager = DataManager()
    
    # Criar disciplinas de exemplo
    disciplinas = [
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Enfermagem Clínica",
            curso="Enfermagem",
            ch_prevista=200.0,
            alunos_previstos=50,
            ch_por_aluno=4.0
        ),
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Estágio em UTI",
            curso="Enfermagem",
            ch_prevista=150.0,
            alunos_previstos=30,
            ch_por_aluno=5.0
        ),
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Clínica Médica",
            curso="Medicina",
            ch_prevista=300.0,
            alunos_previstos=40,
            ch_por_aluno=7.5
        ),
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Pediatria",
            curso="Medicina",
            ch_prevista=250.0,
            alunos_previstos=35,
            ch_por_aluno=7.0
        ),
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Psicologia Clínica",
            curso="Psicologia",
            ch_prevista=180.0,
            alunos_previstos=25,
            ch_por_aluno=7.2
        ),
        Disciplina(
            id=str(uuid.uuid4()),
            nome="Fisioterapia Neurológica",
            curso="Fisioterapia",
            ch_prevista=160.0,
            alunos_previstos=20,
            ch_por_aluno=8.0
        )
    ]
    
    # Salvar disciplinas
    data_manager.save_disciplinas(disciplinas)
    print("✅ Disciplinas criadas com sucesso!")
    
    # Criar campus de exemplo
    campus_list = []
    
    # Campus Central
    campus_central = Campus(
        id=str(uuid.uuid4()),
        nome="Campus Central",
        disciplinas=[d.id for d in disciplinas[:4]]  # Enfermagem, UTI, Clínica Médica, Pediatria
    )
    
    # Adicionar dados reais para Campus Central
    campus_central.dados_reais = {
        disciplinas[0].id: DadosReaisCampus(  # Enfermagem Clínica
            disciplina_id=disciplinas[0].id,
            alunos_reais=45,
            ch_real_total=0.0,  # Será calculado automaticamente
            observacoes="Redução de 5 alunos devido a desistências"
        ),
        disciplinas[1].id: DadosReaisCampus(  # Estágio em UTI
            disciplina_id=disciplinas[1].id,
            alunos_reais=35,
            ch_real_total=180.0,  # CH maior que o calculado
            observacoes="Demanda maior que previsto, necessário reforço"
        ),
        disciplinas[2].id: DadosReaisCampus(  # Clínica Médica
            disciplina_id=disciplinas[2].id,
            alunos_reais=38,
            ch_real_total=0.0,
            observacoes="Dentro do esperado"
        ),
        disciplinas[3].id: DadosReaisCampus(  # Pediatria
            disciplina_id=disciplinas[3].id,
            alunos_reais=30,
            ch_real_total=0.0,
            observacoes="Ligeira redução de alunos"
        )
    }
    
    campus_list.append(campus_central)
    
    # Campus Norte
    campus_norte = Campus(
        id=str(uuid.uuid4()),
        nome="Campus Norte",
        disciplinas=[disciplinas[0].id, disciplinas[4].id, disciplinas[5].id]  # Enfermagem, Psicologia, Fisioterapia
    )
    
    # Adicionar dados reais para Campus Norte
    campus_norte.dados_reais = {
        disciplinas[0].id: DadosReaisCampus(  # Enfermagem Clínica
            disciplina_id=disciplinas[0].id,
            alunos_reais=55,
            ch_real_total=0.0,
            observacoes="Turma maior que previsto"
        ),
        disciplinas[4].id: DadosReaisCampus(  # Psicologia Clínica
            disciplina_id=disciplinas[4].id,
            alunos_reais=22,
            ch_real_total=0.0,
            observacoes="Dentro do planejado"
        ),
        disciplinas[5].id: DadosReaisCampus(  # Fisioterapia Neurológica
            disciplina_id=disciplinas[5].id,
            alunos_reais=15,
            ch_real_total=130.0,  # Menor que previsto
            observacoes="Alguns preceptores em licença médica"
        )
    }
    
    campus_list.append(campus_norte)
    
    # Campus Sul
    campus_sul = Campus(
        id=str(uuid.uuid4()),
        nome="Campus Sul",
        disciplinas=[disciplinas[2].id, disciplinas[3].id, disciplinas[4].id]  # Clínica Médica, Pediatria, Psicologia
    )
    
    # Adicionar dados reais para Campus Sul
    campus_sul.dados_reais = {
        disciplinas[2].id: DadosReaisCampus(  # Clínica Médica
            disciplina_id=disciplinas[2].id,
            alunos_reais=42,
            ch_real_total=320.0,  # Ligeiramente maior
            observacoes="Demanda extra por práticas especializadas"
        ),
        disciplinas[3].id: DadosReaisCampus(  # Pediatria
            disciplina_id=disciplinas[3].id,
            alunos_reais=33,
            ch_real_total=0.0,
            observacoes="Número próximo ao previsto"
        ),
        disciplinas[4].id: DadosReaisCampus(  # Psicologia Clínica
            disciplina_id=disciplinas[4].id,
            alunos_reais=28,
            ch_real_total=0.0,
            observacoes="Aumento de demanda local"
        )
    }
    
    campus_list.append(campus_sul)
    
    # Salvar campus
    data_manager.save_campus(campus_list)
    print("✅ Campus criados com sucesso!")
    
    print("\n📊 Dados de exemplo criados:")
    print(f"• {len(disciplinas)} disciplinas")
    print(f"• {len(campus_list)} campus")
    print("• Dados reais preenchidos para demonstração")
    print("\n🚀 Execute 'streamlit run app.py' para ver o dashboard!")

if __name__ == "__main__":
    criar_dados_exemplo()