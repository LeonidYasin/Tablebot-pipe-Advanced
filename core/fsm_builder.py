# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys  
from aiogram.fsm.state import State, StatesGroup

def create_fsm_from_states(states_found):
    """Создает класс FSM с динамическими состояниями"""
    class DynFSM(StatesGroup):
        pass

    for state_name in states_found:
        setattr(DynFSM, state_name, State())
    
    print(f"[fsm_builder] 🧠 Создано FSM с {len(states_found)} состояниями", file=sys.stderr)
    return DynFSM

def extract_states_from_table(rows):
    """Извлекает уникальные состояния из таблицы"""
    states_found = {r["from_state"] for r in rows} | {r["to_state"] for r in rows}
    states_found = {s for s in states_found if s and s != "—"}
    print(f"[fsm_builder] 🔍 Извлечено состояний: {len(states_found)}", file=sys.stderr)
    return states_found