import pkgutil
import inspect
import importlib

from pathlib import Path

from app.ai.providers.base import AIProvider
from app.core.config import settings, _is_placeholder_value


class ProviderLoader:

    def load_all(self):

        providers = []
        loaded_provider_names = set()

        enabled_public_providers = {
            name.strip().lower()
            for name in (
                (settings.PUBLIC_PROVIDERS or "")
                .split(",")
            )
            if name.strip()
        }

        required_key_map = {
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "openai": "OPENAI_API_KEY",
        }

        provider_path = (
            Path(__file__)
            .parent
            .parent
            / "providers"
        )

        package = (
            "app.ai.providers"
        )

        for module_info in (
            pkgutil.iter_modules(
                [str(provider_path)]
            )
        ):

            module_name = (
                module_info.name
            )

            if module_name in (
                "base",
                "__pycache__",
                "mock",
                "ollama_provider"
            ):
                continue

            try:

                module = (
                    importlib.import_module(
                        f"{package}.{module_name}"
                    )
                )

            except Exception as e:

                print()
                print("# --------------------------------")
                print("[ERROR] PROVIDER IMPORT FAIL")
                print("# --------------------------------")
                print(module_name)
                print(str(e))
                print("# --------------------------------")
                print()

                continue

            for _, obj in (
                inspect.getmembers(
                    module,
                    inspect.isclass
                )
            ):

                try:

                    if (
                        issubclass(
                            obj,
                            AIProvider
                        )
                        and obj is not AIProvider
                    ):

                        provider_name = str(obj.__name__).replace("Provider", "").strip().lower()

                        if provider_name not in enabled_public_providers:
                            continue

                        required_key_name = required_key_map.get(provider_name)
                        key_value = getattr(settings, required_key_name, None) if required_key_name else None
                        if required_key_name and (
                            not key_value or _is_placeholder_value(key_value)
                        ):
                            print()
                            print("# --------------------------------")
                            print("# PROVIDER SKIPPED (missing/placeholder API key)")
                            print("# --------------------------------")
                            print(provider_name)
                            print("# --------------------------------")
                            print()
                            continue

                        instance = obj()
                        provider_name = str(instance.name).strip().lower()

                        if (
                            provider_name
                            in loaded_provider_names
                        ):

                            print()
                            print("# --------------------------------")
                            print("# PROVIDER DUPLICATED")
                            print("# --------------------------------")
                            print(provider_name)
                            print("# --------------------------------")
                            print()

                            continue

                        providers.append(
                            instance
                        )

                        loaded_provider_names.add(
                            provider_name
                        )

                        print()
                        print("# --------------------------------")
                        print("# PROVIDER LOADED")
                        print("# --------------------------------")
                        print(provider_name)
                        print("# --------------------------------")
                        print()

                except Exception as e:

                    print()
                    print("# --------------------------------")
                    print("[ERROR] PROVIDER CREATE FAIL")
                    print("# --------------------------------")
                    print(obj)
                    print(str(e))
                    print("# --------------------------------")
                    print()

        print()
        print("# --------------------------------")
        print("# REGISTERED PROVIDERS")
        print("# --------------------------------")

        for provider in providers:

            print(
                provider.name
            )

        print("# --------------------------------")
        print()

        return providers
