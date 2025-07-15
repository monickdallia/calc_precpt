import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid

from models import Disciplina, Campus, DataManager, DadosReaisCampus
from utils import calcular_resultados, gerar_relatorio_excel, calcular_metricas_resumo

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Preceptores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar o gerenciador de dados
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-excesso {
        color: #d62728;
        font-weight: bold;
    }
    .status-falta {
        color: #ff7f0e;
        font-weight: bold;
    }
    .status-adequado {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 Calculadora de Carga Horária - Preceptores de Estágio")
    st.markdown("**Sistema de Gestão de Preceptores por Campus e Disciplina**")
    
    # Sidebar para navegação
    with st.sidebar:
        st.header("🧭 Navegação")
        page = st.selectbox(
            "Selecione a página:",
            ["🏠 Dashboard", "⚙️ Configuração Corporativa", "🏫 Dados por Campus", "📋 Relatórios"]
        )
        
        st.markdown("---")
        st.markdown("### 📖 Como usar:")
        st.markdown("""
        1. **Configuração Corporativa**: Defina disciplinas, cursos e dados previstos
        2. **Dados por Campus**: Cada campus preenche dados reais
        3. **Dashboard**: Visualize métricas e análises
        4. **Relatórios**: Gere relatórios Excel
        """)
    
    # Carregar dados
    disciplinas = data_manager.load_disciplinas()
    campus_list = data_manager.load_campus()
    
    if page == "🏠 Dashboard":
        show_dashboard(disciplinas, campus_list)
    elif page == "⚙️ Configuração Corporativa":
        show_configuracao_corporativa(disciplinas, campus_list)
    elif page == "🏫 Dados por Campus":
        show_dados_campus(disciplinas, campus_list)
    elif page == "📋 Relatórios":
        show_relatorios(disciplinas, campus_list)

def show_dashboard(disciplinas, campus_list):
    st.header("🏠 Dashboard - Visão Geral")
    
    if not disciplinas or not campus_list:
        st.warning("⚠️ Configure primeiro as disciplinas e campus nas páginas de configuração.")
        return
    
    # Calcular resultados
    resultados = calcular_resultados(disciplinas, campus_list)
    
    if not resultados:
        st.info("ℹ️ Nenhum dado encontrado. Verifique se os campus têm disciplinas associadas.")
        return
    
    # Métricas resumo
    metricas = calcular_metricas_resumo(resultados)
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "CH Total Prevista",
            f"{metricas['total_ch_prevista']:.1f}h",
            delta=None
        )
    
    with col2:
        st.metric(
            "CH Total Real",
            f"{metricas['total_ch_real']:.1f}h",
            delta=f"{metricas['diferenca_ch_total']:.1f}h"
        )
    
    with col3:
        st.metric(
            "Eficiência Geral",
            f"{metricas['eficiencia_geral']:.1f}%",
            delta=f"{metricas['eficiencia_geral'] - 100:.1f}pp"
        )
    
    with col4:
        st.metric(
            "Oportunidades de Economia",
            f"{metricas['oportunidades_economia']:.1f}h",
            delta=None,
            help="Horas que podem ser reduzidas (disciplinas em excesso)"
        )
    
    st.markdown("---")
    
    # Resumo por status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔴 Disciplinas em Excesso")
        st.metric("Quantidade", metricas['disciplinas_excesso'])
        st.metric("CH em Excesso", f"{metricas['ch_excesso']:.1f}h")
    
    with col2:
        st.markdown("### 🟡 Disciplinas em Falta")
        st.metric("Quantidade", metricas['disciplinas_falta'])
        st.metric("CH em Falta", f"{metricas['ch_falta']:.1f}h")
    
    with col3:
        st.markdown("### 🟢 Disciplinas Adequadas")
        st.metric("Quantidade", metricas['disciplinas_adequadas'])
        st.metric("% do Total", f"{(metricas['disciplinas_adequadas']/metricas['disciplinas_total']*100):.1f}%")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por campus
        df_resultados = pd.DataFrame([
            {
                "Campus": r.campus,
                "Curso": r.curso,
                "Disciplina": r.disciplina_nome,
                "CH Prevista": r.ch_prevista,
                "CH Real": r.ch_real,
                "Diferença": r.diferenca_ch,
                "Status": r.status
            }
            for r in resultados
        ])
        
        resumo_campus = df_resultados.groupby('Campus').agg({
            'CH Prevista': 'sum',
            'CH Real': 'sum',
            'Diferença': 'sum'
        }).reset_index()
        
        fig_campus = px.bar(
            resumo_campus,
            x='Campus',
            y=['CH Prevista', 'CH Real'],
            title="Carga Horária por Campus",
            barmode='group'
        )
        st.plotly_chart(fig_campus, use_container_width=True)
    
    with col2:
        # Gráfico de pizza do status
        status_counts = df_resultados['Status'].value_counts()
        colors = {'Excesso': '#d62728', 'Falta': '#ff7f0e', 'Adequado': '#2ca02c'}
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição por Status",
            color=status_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("### 📋 Detalhamento por Disciplina")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        campus_filter = st.selectbox("Filtrar por Campus", ["Todos"] + list(df_resultados['Campus'].unique()))
    with col2:
        curso_filter = st.selectbox("Filtrar por Curso", ["Todos"] + list(df_resultados['Curso'].unique()))
    with col3:
        status_filter = st.selectbox("Filtrar por Status", ["Todos"] + list(df_resultados['Status'].unique()))
    
    # Aplicar filtros
    df_filtered = df_resultados.copy()
    if campus_filter != "Todos":
        df_filtered = df_filtered[df_filtered['Campus'] == campus_filter]
    if curso_filter != "Todos":
        df_filtered = df_filtered[df_filtered['Curso'] == curso_filter]
    if status_filter != "Todos":
        df_filtered = df_filtered[df_filtered['Status'] == status_filter]
    
    # Colorir a tabela baseado no status
    def color_status(val):
        if val == 'Excesso':
            return 'background-color: #ffebee'
        elif val == 'Falta':
            return 'background-color: #fff3e0'
        elif val == 'Adequado':
            return 'background-color: #e8f5e8'
        return ''
    
    styled_df = df_filtered.style.applymap(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)

def show_configuracao_corporativa(disciplinas, campus_list):
    st.header("⚙️ Configuração Corporativa")
    st.markdown("**Área restrita para configuração de dados previstos**")
    
    tab1, tab2 = st.tabs(["📚 Disciplinas", "🏫 Campus"])
    
    with tab1:
        st.subheader("Gestão de Disciplinas")
        
        # Formulário para nova disciplina
        with st.expander("➕ Adicionar Nova Disciplina", expanded=False):
            with st.form("nova_disciplina"):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome da Disciplina*")
                    curso = st.text_input("Curso*")
                    ch_prevista = st.number_input("CH Prevista (horas)*", min_value=0.0, step=0.5)
                
                with col2:
                    alunos_previstos = st.number_input("Alunos Previstos*", min_value=0, step=1)
                    ch_por_aluno = st.number_input("CH por Aluno (horas)*", min_value=0.0, step=0.1)
                
                submitted = st.form_submit_button("Adicionar Disciplina")
                
                if submitted:
                    if nome and curso and ch_prevista > 0 and ch_por_aluno > 0:
                        nova_disciplina = Disciplina(
                            id=str(uuid.uuid4()),
                            nome=nome,
                            curso=curso,
                            ch_prevista=ch_prevista,
                            alunos_previstos=alunos_previstos,
                            ch_por_aluno=ch_por_aluno
                        )
                        disciplinas.append(nova_disciplina)
                        data_manager.save_disciplinas(disciplinas)
                        st.success("✅ Disciplina adicionada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Preencha todos os campos obrigatórios.")
        
        # Lista de disciplinas existentes
        if disciplinas:
            st.subheader("Disciplinas Cadastradas")
            for i, disc in enumerate(disciplinas):
                with st.expander(f"{disc.nome} - {disc.curso}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**CH Prevista:** {disc.ch_prevista}h")
                        st.write(f"**Alunos Previstos:** {disc.alunos_previstos}")
                    
                    with col2:
                        st.write(f"**CH por Aluno:** {disc.ch_por_aluno}h")
                        st.write(f"**CH Total Estimada:** {disc.alunos_previstos * disc.ch_por_aluno}h")
                    
                    with col3:
                        if st.button("🗑️ Remover", key=f"remove_disc_{i}"):
                            disciplinas.pop(i)
                            data_manager.save_disciplinas(disciplinas)
                            st.success("Disciplina removida!")
                            st.rerun()
        else:
            st.info("ℹ️ Nenhuma disciplina cadastrada ainda.")
    
    with tab2:
        st.subheader("Gestão de Campus")
        
        # Formulário para novo campus
        with st.expander("➕ Adicionar Novo Campus", expanded=False):
            with st.form("novo_campus"):
                nome_campus = st.text_input("Nome do Campus*")
                disciplinas_selecionadas = st.multiselect(
                    "Disciplinas oferecidas neste campus:",
                    options=[f"{d.nome} - {d.curso}" for d in disciplinas],
                    help="Selecione quais disciplinas são oferecidas neste campus"
                )
                
                submitted = st.form_submit_button("Adicionar Campus")
                
                if submitted:
                    if nome_campus:
                        # Mapear nomes selecionados para IDs
                        disc_ids = []
                        for disc_nome in disciplinas_selecionadas:
                            for disc in disciplinas:
                                if f"{disc.nome} - {disc.curso}" == disc_nome:
                                    disc_ids.append(disc.id)
                                    break
                        
                        novo_campus = Campus(
                            id=str(uuid.uuid4()),
                            nome=nome_campus,
                            disciplinas=disc_ids
                        )
                        campus_list.append(novo_campus)
                        data_manager.save_campus(campus_list)
                        st.success("✅ Campus adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Preencha o nome do campus.")
        
        # Lista de campus existentes
        if campus_list:
            st.subheader("Campus Cadastrados")
            for i, campus in enumerate(campus_list):
                with st.expander(f"🏫 {campus.nome}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if campus.disciplinas:
                            st.write("**Disciplinas oferecidas:**")
                            for disc_id in campus.disciplinas:
                                disc = next((d for d in disciplinas if d.id == disc_id), None)
                                if disc:
                                    st.write(f"• {disc.nome} - {disc.curso}")
                        else:
                            st.write("Nenhuma disciplina associada.")
                    
                    with col2:
                        if st.button("🗑️ Remover", key=f"remove_campus_{i}"):
                            campus_list.pop(i)
                            data_manager.save_campus(campus_list)
                            st.success("Campus removido!")
                            st.rerun()
        else:
            st.info("ℹ️ Nenhum campus cadastrado ainda.")

def show_dados_campus(disciplinas, campus_list):
    st.header("🏫 Dados por Campus")
    st.markdown("**Área para preenchimento de dados reais por campus**")
    
    if not campus_list:
        st.warning("⚠️ Nenhum campus cadastrado. Configure primeiro na aba 'Configuração Corporativa'.")
        return
    
    # Selecionar campus
    campus_nomes = [c.nome for c in campus_list]
    campus_selecionado = st.selectbox("Selecione o Campus:", campus_nomes)
    
    if campus_selecionado:
        campus = next(c for c in campus_list if c.nome == campus_selecionado)
        
        st.subheader(f"📝 Preenchimento de Dados - {campus.nome}")
        
        if not campus.disciplinas:
            st.warning("⚠️ Este campus não possui disciplinas associadas.")
            return
        
        # Formulário para cada disciplina
        for disc_id in campus.disciplinas:
            disciplina = next((d for d in disciplinas if d.id == disc_id), None)
            if not disciplina:
                continue
            
            with st.expander(f"📚 {disciplina.nome} - {disciplina.curso}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Dados Previstos:**")
                    st.write(f"• CH Prevista: {disciplina.ch_prevista}h")
                    st.write(f"• Alunos Previstos: {disciplina.alunos_previstos}")
                    st.write(f"• CH por Aluno: {disciplina.ch_por_aluno}h")
                
                with col2:
                    st.markdown("**Dados Reais:**")
                    
                    # Dados atuais
                    dados_atuais = campus.dados_reais.get(disc_id, DadosReaisCampus(disc_id))
                    
                    with st.form(f"dados_{disc_id}"):
                        alunos_reais = st.number_input(
                            "Quantidade de Alunos Real:",
                            min_value=0,
                            value=dados_atuais.alunos_reais,
                            step=1,
                            key=f"alunos_{disc_id}"
                        )
                        
                        ch_real_total = st.number_input(
                            "CH Real Total (opcional):",
                            min_value=0.0,
                            value=dados_atuais.ch_real_total,
                            step=0.5,
                            help="Se não preenchido, será calculado automaticamente: Alunos × CH por Aluno",
                            key=f"ch_{disc_id}"
                        )
                        
                        observacoes = st.text_area(
                            "Observações:",
                            value=dados_atuais.observacoes,
                            key=f"obs_{disc_id}"
                        )
                        
                        submitted = st.form_submit_button("💾 Salvar Dados")
                        
                        if submitted:
                            campus.dados_reais[disc_id] = DadosReaisCampus(
                                disciplina_id=disc_id,
                                alunos_reais=alunos_reais,
                                ch_real_total=ch_real_total,
                                observacoes=observacoes
                            )
                            data_manager.save_campus(campus_list)
                            st.success("✅ Dados salvos com sucesso!")
                            st.rerun()
                
                # Mostrar cálculo automático
                dados_atual = campus.dados_reais.get(disc_id, DadosReaisCampus(disc_id))
                ch_calculada = dados_atual.alunos_reais * disciplina.ch_por_aluno
                ch_final = dados_atual.ch_real_total if dados_atual.ch_real_total > 0 else ch_calculada
                diferenca = ch_final - disciplina.ch_prevista
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CH Calculada", f"{ch_calculada:.1f}h")
                with col2:
                    st.metric("CH Final", f"{ch_final:.1f}h")
                with col3:
                    delta_color = "normal" if abs(diferenca) <= disciplina.ch_prevista * 0.05 else "off"
                    st.metric("Diferença", f"{diferenca:.1f}h", delta=f"{diferenca:.1f}h")

def show_relatorios(disciplinas, campus_list):
    st.header("📋 Relatórios e Análises")
    
    if not disciplinas or not campus_list:
        st.warning("⚠️ Configure primeiro as disciplinas e campus.")
        return
    
    # Calcular resultados
    resultados = calcular_resultados(disciplinas, campus_list)
    
    if not resultados:
        st.info("ℹ️ Nenhum dado encontrado para gerar relatórios.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Análise de Oportunidades")
        
        # Disciplinas em excesso (oportunidades de desligamento)
        excesso = [r for r in resultados if r.status == "Excesso"]
        if excesso:
            st.markdown("### 🔴 Oportunidades de Desligamento")
            excesso_sorted = sorted(excesso, key=lambda x: x.diferenca_ch, reverse=True)
            
            for r in excesso_sorted[:10]:  # Top 10
                st.markdown(f"""
                **{r.disciplina_nome}** ({r.curso}) - *{r.campus}*  
                💰 Economia potencial: **{r.diferenca_ch:.1f}h** ({r.diferenca_ch/40:.1f} professores equivalentes)  
                📊 Eficiência: {r.eficiencia:.1f}%
                """)
        
        # Disciplinas em falta (necessidades de contratação)
        falta = [r for r in resultados if r.status == "Falta"]
        if falta:
            st.markdown("### 🟡 Necessidades de Contratação")
            falta_sorted = sorted(falta, key=lambda x: x.diferenca_ch)
            
            for r in falta_sorted[:10]:  # Top 10
                st.markdown(f"""
                **{r.disciplina_nome}** ({r.curso}) - *{r.campus}*  
                📈 Necessidade: **{abs(r.diferenca_ch):.1f}h** ({abs(r.diferenca_ch)/40:.1f} professores equivalentes)  
                📊 Eficiência: {r.eficiencia:.1f}%
                """)
    
    with col2:
        st.subheader("📥 Exportar Dados")
        
        if st.button("📊 Gerar Relatório Excel", type="primary"):
            try:
                filename = gerar_relatorio_excel(resultados, f"relatorio_preceptores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
                
                with open(filename, "rb") as file:
                    st.download_button(
                        label="⬇️ Baixar Relatório Excel",
                        data=file.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.success("✅ Relatório gerado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📋 O relatório Excel contém:")
        st.markdown("""
        - **Relatório Geral**: Todos os dados detalhados
        - **Resumo por Campus**: Totais consolidados
        - **Oportunidades Desligamento**: Disciplinas em excesso
        - **Necessidades Contratação**: Disciplinas em falta
        """)

if __name__ == "__main__":
    main()