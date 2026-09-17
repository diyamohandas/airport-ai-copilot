import json
import os
from datetime import datetime


MEMORY_PATH = "data/memory/long_term_memory.json"


class ConversationMemory:
    """
    Handles short-term and long-term memory for the
    Airport Operations AI Copilot.
    """

    def __init__(self, memory_path=MEMORY_PATH):
        self.memory_path = memory_path

        # Short-term memory exists only for the current session.
        self.short_term_memory = []

        # Ensure memory directory exists.
        os.makedirs(
            os.path.dirname(self.memory_path),
            exist_ok=True
        )

        # Load long-term memory from disk.
        self.long_term_memory = self._load_long_term_memory()

    # ---------------------------------------------------------
    # SHORT-TERM MEMORY
    # ---------------------------------------------------------

    def add_message(self, role, content):
        """
        Add a message to the current conversation.
        """

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self.short_term_memory.append(message)

    def get_short_term_memory(self):
        """
        Return the current conversation history.
        """

        return self.short_term_memory

    def clear_short_term_memory(self):
        """
        Clear the current conversation.
        """

        self.short_term_memory = []

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    def _load_long_term_memory(self):
        """
        Load persistent memory from disk.
        """

        if not os.path.exists(self.memory_path):
            return []

        try:
            with open(
                self.memory_path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return []

    def add_long_term_memory(
        self,
        airport_code,
        memory_type,
        content,
    ):
        """
        Store useful information that should persist
        across sessions.
        """

        memory = {
            "airport_code": airport_code,
            "memory_type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self.long_term_memory.append(memory)

        self._save_long_term_memory()

        return memory

    def get_long_term_memory(self, airport_code=None):
        """
        Retrieve persistent memories.

        If airport_code is provided, only memories
        for that airport are returned.
        """

        if airport_code is None:
            return self.long_term_memory

        return [
            memory
            for memory in self.long_term_memory
            if memory.get("airport_code") == airport_code
        ]

    def _save_long_term_memory(self):
        """
        Save long-term memory to disk.
        """

        with open(
            self.memory_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.long_term_memory,
                file,
                indent=2,
            )


if __name__ == "__main__":

    print("=" * 70)
    print("MEMORY TEST")
    print("=" * 70)

    memory = ConversationMemory()

    # ---------------------------------------------------------
    # Test short-term memory
    # ---------------------------------------------------------

    print("\nSHORT-TERM MEMORY")

    memory.add_message(
        "user",
        "SFO is experiencing high cancellation rates."
    )

    memory.add_message(
        "assistant",
        "I will investigate the current SFO operational metrics."
    )

    print(json.dumps(
        memory.get_short_term_memory(),
        indent=2
    ))

    # ---------------------------------------------------------
    # Test long-term memory
    # ---------------------------------------------------------

    print("\nLONG-TERM MEMORY")

    memory.add_long_term_memory(
        airport_code="SFO",
        memory_type="operational_issue",
        content=(
            "SFO experienced elevated cancellation rates "
            "during the morning operational period."
        ),
    )

    memories = memory.get_long_term_memory("SFO")

    print(json.dumps(
        memories,
        indent=2
    ))

    print("\nMemory test completed successfully.")
