from datetime import date


class Receita:
    def __init__(self, data_emissao: date, validade: date,
                 od_esferico: float, oe_esferico: float,
                 id_cliente: int, crm_medico: str,
                 od_cilindrico: float = None, od_eixo: int = None,
                 oe_cilindrico: float = None, oe_eixo: int = None,
                 id_receita: int = None):
        if validade <= data_emissao:
            raise ValueError("Validade da receita deve ser posterior à emissão.")
        self.id_receita = id_receita
        self.data_emissao = data_emissao
        self.validade = validade
        self.od_esferico = od_esferico
        self.od_cilindrico = od_cilindrico
        self.od_eixo = od_eixo
        self.oe_esferico = oe_esferico
        self.oe_cilindrico = oe_cilindrico
        self.oe_eixo = oe_eixo
        self.id_cliente = id_cliente
        self.crm_medico = crm_medico

    def esta_valida(self, referencia: date = None) -> bool:
        referencia = referencia or date.today()
        return referencia <= self.validade

    def __str__(self):
        situacao = "válida" if self.esta_valida() else "vencida"
        return (f"Receita #{self.id_receita} | Cliente {self.id_cliente} | "
                f"CRM {self.crm_medico} | válida até {self.validade} ({situacao})")
