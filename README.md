
# 📊 Avaliação de Fluência — Dashboard v6 (com Auditoria Automática)

Fluxo:
1) Upload do Excel (aba 'Consolidação')
2) Auditoria automática (fórmulas/erros) — relatórios salvos na MESMA pasta do arquivo
3) Continuação automática (sem bloqueio)
4) Tabelas e gráficos:
   - % Com Data por GRE (barras horizontais, verde >= 70%, vermelho < 70%)
   - % Com Data por Município (dentro da GRE selecionada)
   - Tabela de Escolas com filtros (GRE, Município, Situação) e download dos faltantes

Para iniciar:
  streamlit run app.py
