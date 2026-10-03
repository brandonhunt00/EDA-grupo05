SELECT
    faixa_etaria,
    sexo,
    COUNT(*) AS total_consultas,
    SUM(CASE WHEN status='NO_SHOW' THEN 1 ELSE 0 END) AS total_no_shows,
    ROUND(100.0 * SUM(CASE WHEN status='NO_SHOW' THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_no_show
FROM agendamentos
WHERE status IN ('REALIZADO','NO_SHOW')
GROUP BY faixa_etaria, sexo
ORDER BY taxa_no_show DESC;
