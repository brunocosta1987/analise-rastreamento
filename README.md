# 🚛 Sistema de Análise Logística de Rastreamento Veicular

Este sistema permite importar planilhas Excel com endereços, feriados e rastreamento de veículos para gerar análises logísticas e detectar ocorrências como:

- Funcionamento fora do horário (após as 18h)
- Funcionamento em feriados e finais de semana
- Presença em endereços de motoristas ou coordenadores

## 📥 Como usar

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute o sistema com Streamlit:
   ```
   streamlit run app.py
   ```

## 📂 Estrutura esperada das planilhas

### Endereços
- Colunas: `Endereço`, `Tipo` (valores: Motorista ou Coordenador)

### Feriados
- Coluna: `Data` (datas dos feriados)

### Rastreamento
- Colunas: `Data da Posição`, `Ignição`, `Velocidade (km/h)`, `Endereço`

## 📊 Saída
- Planilha Excel com as ocorrências encontradas
- Gráficos interativos com Plotly
