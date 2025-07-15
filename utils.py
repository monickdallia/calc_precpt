from typing import List, Dict
import pandas as pd
from models import Disciplina, Campus, CalculoResultado, DadosReaisCampus

def calcular_resultados(disciplinas: List[Disciplina], campus_list: List[Campus]) -> List[CalculoResultado]:
    """
    Calcula os resultados comparando dados previstos vs reais
    """
    resultados = []
    
    # Criar um dicionário de disciplinas para facilitar consulta
    disc_dict = {d.id: d for d in disciplinas}
    
    for campus in campus_list:
        for disc_id in campus.disciplinas:
            if disc_id not in disc_dict:
                continue
                
            disciplina = disc_dict[disc_id]
            dados_reais = campus.dados_reais.get(disc_id, DadosReaisCampus(disc_id))
            
            # Calcular CH real baseada nos alunos reais
            ch_real_calculada = dados_reais.alunos_reais * disciplina.ch_por_aluno
            
            # Usar CH real informada ou calculada
            ch_real = dados_reais.ch_real_total if dados_reais.ch_real_total > 0 else ch_real_calculada
            
            # Calcular diferenças
            diferenca_ch = ch_real - disciplina.ch_prevista
            diferenca_alunos = dados_reais.alunos_reais - disciplina.alunos_previstos
            
            # Calcular eficiência
            eficiencia = (ch_real / disciplina.ch_prevista * 100) if disciplina.ch_prevista > 0 else 0
            
            # Determinar status
            if abs(diferenca_ch) <= (disciplina.ch_prevista * 0.05):  # 5% de tolerância
                status = "Adequado"
            elif diferenca_ch > 0:
                status = "Excesso"
            else:
                status = "Falta"
            
            resultado = CalculoResultado(
                disciplina_id=disc_id,
                disciplina_nome=disciplina.nome,
                curso=disciplina.curso,
                campus=campus.nome,
                ch_prevista=disciplina.ch_prevista,
                ch_real=ch_real,
                diferenca_ch=diferenca_ch,
                alunos_previstos=disciplina.alunos_previstos,
                alunos_reais=dados_reais.alunos_reais,
                diferenca_alunos=diferenca_alunos,
                eficiencia=eficiencia,
                status=status
            )
            
            resultados.append(resultado)
    
    return resultados

def gerar_relatorio_excel(resultados: List[CalculoResultado], filename: str = "relatorio_preceptores.xlsx"):
    """
    Gera um relatório em Excel com os resultados
    """
    # Converter para DataFrame
    data = []
    for r in resultados:
        data.append({
            "Campus": r.campus,
            "Curso": r.curso,
            "Disciplina": r.disciplina_nome,
            "CH Prevista": r.ch_prevista,
            "CH Real": r.ch_real,
            "Diferença CH": r.diferenca_ch,
            "Alunos Previstos": r.alunos_previstos,
            "Alunos Reais": r.alunos_reais,
            "Diferença Alunos": r.diferenca_alunos,
            "Eficiência %": r.eficiencia,
            "Status": r.status
        })
    
    df = pd.DataFrame(data)
    
    # Criar arquivo Excel com múltiplas abas
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Aba principal com todos os dados
        df.to_excel(writer, sheet_name='Relatório Geral', index=False)
        
        # Aba com resumo por campus
        resumo_campus = df.groupby('Campus').agg({
            'CH Prevista': 'sum',
            'CH Real': 'sum',
            'Diferença CH': 'sum',
            'Alunos Previstos': 'sum',
            'Alunos Reais': 'sum'
        }).reset_index()
        resumo_campus['Eficiência %'] = (resumo_campus['CH Real'] / resumo_campus['CH Prevista'] * 100).round(2)
        resumo_campus.to_excel(writer, sheet_name='Resumo por Campus', index=False)
        
        # Aba com disciplinas em excesso (oportunidades de desligamento)
        excesso = df[df['Status'] == 'Excesso'].sort_values('Diferença CH', ascending=False)
        excesso.to_excel(writer, sheet_name='Oportunidades Desligamento', index=False)
        
        # Aba com disciplinas em falta
        falta = df[df['Status'] == 'Falta'].sort_values('Diferença CH')
        falta.to_excel(writer, sheet_name='Necessidades Contratação', index=False)
    
    return filename

def calcular_metricas_resumo(resultados: List[CalculoResultado]) -> Dict:
    """
    Calcula métricas resumo para o dashboard
    """
    if not resultados:
        return {}
    
    total_ch_prevista = sum(r.ch_prevista for r in resultados)
    total_ch_real = sum(r.ch_real for r in resultados)
    total_alunos_previstos = sum(r.alunos_previstos for r in resultados)
    total_alunos_reais = sum(r.alunos_reais for r in resultados)
    
    disciplinas_excesso = [r for r in resultados if r.status == "Excesso"]
    disciplinas_falta = [r for r in resultados if r.status == "Falta"]
    disciplinas_adequadas = [r for r in resultados if r.status == "Adequado"]
    
    ch_excesso = sum(r.diferenca_ch for r in disciplinas_excesso)
    ch_falta = abs(sum(r.diferenca_ch for r in disciplinas_falta))
    
    return {
        "total_ch_prevista": total_ch_prevista,
        "total_ch_real": total_ch_real,
        "diferenca_ch_total": total_ch_real - total_ch_prevista,
        "total_alunos_previstos": total_alunos_previstos,
        "total_alunos_reais": total_alunos_reais,
        "eficiencia_geral": (total_ch_real / total_ch_prevista * 100) if total_ch_prevista > 0 else 0,
        "disciplinas_total": len(resultados),
        "disciplinas_excesso": len(disciplinas_excesso),
        "disciplinas_falta": len(disciplinas_falta),
        "disciplinas_adequadas": len(disciplinas_adequadas),
        "ch_excesso": ch_excesso,
        "ch_falta": ch_falta,
        "oportunidades_economia": ch_excesso  # Horas que podem ser reduzidas
    }