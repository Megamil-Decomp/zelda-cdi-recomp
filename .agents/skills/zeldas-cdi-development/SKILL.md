---
name: zeldas-cdi-development
description: "Retomar tarefas, alterar fontes e preparar entregas no Zelda CD-i, preservando candidatos aceitos, mídia e proveniência. Usar para desenvolvimento deste repositório; análise REA e diagnóstico de runtime têm skills específicas."
---

# Desenvolvimento Zelda CD-i

Ler [AGENTS](../../../AGENTS.md) e [handoff](../../../docs/AI_HANDOFF.md), depois o pedido atual e os registros recentes. O briefing original e marcos antigos são históricos; não reiniciar M0 nem presumir que um clone público contém os candidatos privados.

O fluxo e o aceite estão em [Development.md](../../../docs/wiki/Development.md). Carregar somente a rota necessária:

- Host/interface: `app/`, headers autorais e patch de integração. Preservar pixels/estado convidados; volume afeta apenas a cópia PCM do host.
- CPU/hardware/emissor: patch reproduzível em staging da revisão auditada, com regressão sintética e cenário privado. Não editar upstream ou arquivos referidos por proveniência aceita sem autorização/isolamento adequados.
- Novas entradas estáticas: usar [REA](../zeldas-cdi-rea/SKILL.md), não confundir pseudocódigo com emissão ou aceitação.
- Candidato/entrega: usar [validação](../zeldas-cdi-validation/SKILL.md), conferir binário empacotado e manter a referência recuperável.

Antes de alteração grande, registrar problema, plano, aceite e testes. Executar `python3 -m unittest discover -s tests -v`, além dos checks pertinentes. Dados de mídia, seeds, logs e código comercial gerado ficam nos diretórios ignorados. Não transformar falta de teste físico em sucesso de software.

Atualizar documentos afetados e issue conforme o critério real. Na entrega informar mudança, testes e limites. Autorizações vêm do pedido/sessão, não desta skill: não instalar globalmente, publicar pacotes, editar upstream ou enviar mensagens por inferência. Não adicionar política genérica ou novas dependências para uma correção pequena.
