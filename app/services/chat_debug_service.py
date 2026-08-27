class ChatDebugService:

    def print_provider(
        self,
        provider: str
    ):

        print()
        print("# --------------------------------")
        print("# SELECTED PROVIDER")
        print("# --------------------------------")
        print(provider)
        print("# --------------------------------")
        print()

    def print_task_type(
        self,
        task_type: str
    ):

        print()
        print("# --------------------------------")
        print("# TASK TYPE")
        print("# --------------------------------")
        print(task_type)
        print("# --------------------------------")
        print()

    def print_trace(
        self,
        trace
    ):

        print()
        print("# --------------------------------")
        print("# PROMPT TRACE")
        print("# --------------------------------")
        print(trace)
        print("# --------------------------------")
        print()

    def print_prompt(
        self,
        prompt: str
    ):

        print()
        print("# --------------------------------")
        print("# LOCAL BRAIN GENERATED PROMPT")
        print("# --------------------------------")
        print(prompt)
        print("# --------------------------------")
        print()
