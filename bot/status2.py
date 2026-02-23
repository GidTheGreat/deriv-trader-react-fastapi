from rich.console import Console
from rich.status import Status
import asyncio

console = Console()
# Detailed status messages
status_messages = {
    "connection": {},  
    "ticks": {},  
    "trades": {},
    "profit_loss": {},
    "progress":{},
    "runtime info":{},
    "account balance":{},
    "proposal":{} 
    
}

async def background_live_updates():
    """Runs non-intrusive status updates in the background."""
    with console.status("Initializing live updates...", spinner="dots") as status:
        while True:
            status.update(render_status())  # Update status message
            await asyncio.sleep(0.5)  # Adjust frequency as needed
            

muted_categories = { }
def render_status():
    """Formats status messages for display with fixed category order and subgrouping."""
    ordered_categories = ["connection","account balance","ticks","proposal","trades","profit_loss","runtime info","progress"]

    lines = []
    for category in ordered_categories:
        if category in muted_categories:  
            continue  
        if category in status_messages:
            messages = status_messages[category]
            if isinstance(messages, dict) and messages:
                lines.append(f"\n===== {category.upper()} =====")  # Section header
                for sub_key, sub_value in messages.items():
                    if isinstance(sub_value, dict) and sub_value:  # ✅ Handles subgroups
                        lines.append(f"  [{sub_key.upper()}]")  # ✅ Subgroup header
                        for key, value in sub_value.items():
                            lines.append(f"    {key}: {value}")  # ✅ Indented subgroup items
                    else:
                        lines.append(f"{sub_key}: {sub_value}")  # ✅ Normal key-value messages

    return "\n".join(lines)  # ✅ Ensures ordered, readable output               