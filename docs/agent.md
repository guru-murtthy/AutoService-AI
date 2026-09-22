# AutoService AI - Autonomous Agent Framework

## Agent Loop
The autonomous agent follows a 7-step control loop:
`OBSERVE -> THINK -> PLAN -> ACT -> VERIFY -> RECORD -> LEARN`

## Tool Registry (13 Schema-Strict Tools)
1. `search_leads`
2. `get_customer`
3. `get_conversation`
4. `create_lead`
5. `update_lead`
6. `calculate_quote`
7. `create_quote`
8. `send_message`
9. `schedule_followup`
10. `cancel_followup`
11. `generate_report`
12. `get_business_metrics`
13. `get_system_health`

## Conway Automaton Bridge
The adapter located in `automaton-adapter/bridge/adapter.py` connects to external Conway Automaton runtime over REST.
If Conway Automaton is offline, the service automatically falls back to internal task worker loop without interruption.
