-- Código a ser usado no Athena --
-- Há a flag se houve atraso, qnt de dias de atraso e a nota de satisfação do cliente

SELECT * FROM "ecommerce_refined_db"."gold_fato_vendas_logistica" limit 10;


SELECT 
    atraso_entrega as pedido_atrasado,
    COUNT(DISTINCT order_id) as volume_pedidos,
    ROUND(AVG(tempo_entrega_dias), 1) as media_dias_para_entrega,
    ROUND(AVG(review_score), 2) as nota_media_cliente
FROM gold_fato_vendas_logistica
WHERE atraso_entrega IS NOT NULL -- Remove pedidos não entregues
GROUP BY atraso_entrega
ORDER BY atraso_entrega;