# Raid Event Report (Mapa 52)

## Resumo
Este relatório descreve as mudanças aplicadas para suportar o evento RAID "O Cerco da Fenda Sombria" (mapa 52),
com controle de janela de horário via script, bloqueio do mapa quando o evento está fechado e ajuste das missões.

## Mudanças principais
- Evento RAID controlado por horário fixo no script (`20:00` até `21:00`), sem dependência do banco de dados.
- Seleção do mapa 52 bloqueada quando o evento está fechado, com mensagem informando o próximo horário.
- Início do jogo bloqueado caso a sala esteja configurada para o mapa 52 e o evento esteja fechado.
- Missões do mapa 52 desativadas automaticamente quando o evento RAID está fechado.
- Mensagens de status do evento continuam sendo exibidas no lobby, na sala e no início da partida.
- Drops do mapa 52 ajustados para itens raros (+4/+5) de múltiplos bot_types com chance aumentada.

## Arquivos modificados
- `GameServer/Controllers/data/raid_event.py`
- `GameServer/Controllers/Room.py`
- `GameServer/Controllers/Missions.py`
- `GameServer/Controllers/data/planet.py`

## Arquivos relacionados (já existentes)
- `GameServer/Controllers/Lobby.py`
- `GameServer/Controllers/Game.py`

## Observações
- Para alterar o horário da raid, ajuste `RAID_OPEN_TIME` e `RAID_CLOSE_TIME` em
  `GameServer/Controllers/data/raid_event.py`.
