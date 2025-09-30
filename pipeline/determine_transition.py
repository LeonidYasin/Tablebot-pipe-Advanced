#!/usr/bin/env python3

import sys

def determine_transition(row, skip_guard):
    """Определяет следующий стейт для перехода"""
    if skip_guard or not row:
        return None
    
    next_state = row.get("to_state")
    if next_state and next_state != "—":
        print(f"[determine_transition] 🔄 Переход: {next_state!r}")
        return next_state
    
    return None