# 📊 Calculadora de Carga Horária - Preceptores de Estágio

Sistema completo para gestão e cálculo de carga horária de preceptores de estágios em múltiplos campus de uma Instituição de Ensino Superior (IES).

## 🎯 Objetivo

Identificar discrepâncias entre carga horária prevista e real de preceptores, possibilitando:
- ✅ Detectar horas em excesso (oportunidades de desligamento)
- ✅ Identificar horas faltantes (necessidades de contratação)
- ✅ Otimizar recursos humanos
- ✅ Gerar relatórios executivos

## 🚀 Funcionalidades

### 📋 Dashboard Principal
- Métricas consolidadas (CH prevista vs real, eficiência geral)
- Visualizações interativas (gráficos por campus, status)
- Tabela detalhada com filtros
- Análise de oportunidades

### ⚙️ Configuração Corporativa
- Cadastro de disciplinas e cursos
- Definição de CH prevista por disciplina
- Gestão de campus e suas disciplinas
- Configuração de CH por aluno

### 🏫 Dados por Campus
- Interface para cada campus preencher dados reais
- Quantidade real de alunos por disciplina
- CH real total (opcional - calculado automaticamente)
- Observações e comentários

### 📊 Relatórios
- Análise de oportunidades de desligamento
- Necessidades de contratação
- Relatório Excel com múltiplas abas
- Métricas de eficiência por professor equivalente

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Passos de Instalação

1. **Clone ou baixe os arquivos do projeto**

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
streamlit run app.py
```

4. **Acesse no navegador:**
```
http://localhost:8501
```

## 📖 Como Usar

### 1. Configuração Inicial (Corporativo)

1. Acesse **"⚙️ Configuração Corporativa"**
2. **Aba Disciplinas:**
   - Adicione disciplinas com:
     - Nome da disciplina
     - Curso
     - CH prevista total
     - Número de alunos previstos
     - CH de preceptoria por aluno
3. **Aba Campus:**
   - Cadastre campus
   - Associe disciplinas a cada campus

### 2. Preenchimento por Campus

1. Acesse **"🏫 Dados por Campus"**
2. Selecione seu campus
3. Para cada disciplina, preencha:
   - Quantidade real de alunos
   - CH real total (opcional)
   - Observações

### 3. Análise de Resultados

1. **Dashboard:** Visualize métricas consolidadas
2. **Relatórios:** Gere análises detalhadas e relatórios Excel

## 📊 Estrutura dos Cálculos

### Fórmulas Principais

```
CH Real Calculada = Alunos Reais × CH por Aluno
CH Final = CH Real Informada OU CH Real Calculada
Diferença = CH Final - CH Prevista
Eficiência = (CH Real / CH Prevista) × 100
```

### Status das Disciplinas

- **🟢 Adequado:** Diferença ≤ 5% da CH prevista
- **🔴 Excesso:** CH real > CH prevista (+ 5% tolerância)
- **🟡 Falta:** CH real < CH prevista (- 5% tolerância)

### Equivalência em Professores

```
Professores Equivalentes = Diferença CH ÷ 40h (jornada padrão)
```

## 📄 Relatórios Excel

O sistema gera relatórios Excel com 4 abas:

1. **Relatório Geral:** Todos os dados detalhados
2. **Resumo por Campus:** Totais consolidados
3. **Oportunidades Desligamento:** Disciplinas em excesso
4. **Necessidades Contratação:** Disciplinas em falta

## 🗂️ Estrutura de Dados

Os dados são armazenados em formato JSON no diretório `data/`:
- `disciplinas.json`: Configurações das disciplinas
- `campus.json`: Dados dos campus e informações reais

## 🔐 Controle de Acesso

- **Configuração Corporativa:** Restrita ao administrativo central
- **Dados por Campus:** Cada campus acessa apenas seus dados
- **Dashboard/Relatórios:** Visualização consolidada

## 📈 Exemplo de Uso

### Cenário: Campus ABC

**Disciplina:** Enfermagem Clínica  
**CH Prevista:** 200h  
**Alunos Previstos:** 50  
**CH por Aluno:** 4h  

**Dados Reais:**  
**Alunos Reais:** 45  
**CH Real:** 180h  

**Resultado:**  
- Diferença: -20h (Falta)
- Eficiência: 90%
- Equivalente: 0.5 professor a contratar

## 🛠️ Tecnologias Utilizadas

- **Frontend:** Streamlit
- **Visualização:** Plotly
- **Dados:** Pandas
- **Relatórios:** OpenPyXL
- **Backend:** Python

## 📞 Suporte

Para dúvidas ou sugestões sobre o sistema, consulte a documentação interna ou entre em contato com a equipe de TI.

---

**Desenvolvido para otimização de recursos humanos em preceptoria de estágios** 🎓