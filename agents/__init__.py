import sys
from pathlib import Path

# Extend agents package search path so submodules under agents/agents/ are discoverable seamlessly
agents_dir = Path(__file__).parent
inner_agents = agents_dir / "agents"

__path__ = [
    str(agents_dir),
    str(inner_agents)
]

if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))
