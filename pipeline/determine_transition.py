# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
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