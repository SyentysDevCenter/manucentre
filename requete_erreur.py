
# cette requette permet de lister les variante ayant une valeur ou un attribut non present dans la liste du produit model

""" select v.att_id, v.prod_id, p.product_tmpl_id , a.name, t.name as valeur,
 at.name,t.attribute_id, l.id as line
                 from product_attribute_value_product_product_rel v
                 left join product_attribute_value t on t.id = v.att_id
                  left join product_product p on v.prod_id = p.id
				  left join product_attribute at on at.id = t.attribute_id
				  left join product_template a on p.product_tmpl_id = a.id
                  LEFT JOIN product_attribute_line l on
				  l.product_tmpl_id = p.product_tmpl_id
				  and l.attribute_id = t.attribute_id
                 where l.id is null and p.active=True
				 order by p.product_tmpl_id, line, t.attribute_id"""
