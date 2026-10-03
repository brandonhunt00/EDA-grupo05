SELECT
    month(data_consulta) AS mes,
    COUNT(*) AS total_consultas,
    SUM(CASE WHEN status='NO_SHOW' THEN 1 ELSE 0 END) AS total_no_shows,
    ROUND(100.0 * SUM(CASE WHEN status='NO_SHOW' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_no_show,
    ROUND(SUM(CASE WHEN status='NO_SHOW' THEN valor_consulta ELSE 0 END), 2) AS impacto_financeiro
FROM agendamentos
WHERE status IN ('REALIZADO','NO_SHOW')
GROUP BY month(data_consulta)
ORDER BY mes;
