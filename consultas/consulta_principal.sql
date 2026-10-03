SELECT
    year(data_consulta) AS ano,
    month(data_consulta) AS mes,
    faixa_etaria,
    sexo,
    unidade_id,
    especialidade,
    COUNT(*) AS total_consultas,
    SUM(CASE WHEN status = 'NO_SHOW' THEN 1 ELSE 0 END) AS total_no_shows,
    ROUND(100.0 * SUM(CASE WHEN status = 'NO_SHOW' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_no_show,
    ROUND(SUM(CASE WHEN status = 'NO_SHOW' THEN valor_consulta ELSE 0 END), 2) AS impacto_financeiro
FROM agendamentos
WHERE status IN ('REALIZADO','NO_SHOW')
GROUP BY year(data_consulta), month(data_consulta), faixa_etaria, sexo, unidade_id, especialidade
ORDER BY impacto_financeiro DESC;
