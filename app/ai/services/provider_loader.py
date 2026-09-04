import pkgutil
import inspect
import importlib

from pathlib import Path

from app.ai.providers.base import AIProvider


class ProviderLoader:

    def load_all(self):

        providers = []
        loaded_provider_names = set()

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
                "mock"
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
                print("# PROVIDER IMPORT FAIL")
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

                        instance = obj()

                        if (
                            instance.name
                            in loaded_provider_names
                        ):

                            print()
                            print("# --------------------------------")
                            print("# PROVIDER DUPLICATED")
                            print("# --------------------------------")
                            print(instance.name)
                            print("# --------------------------------")
                            print()

                            continue

                        providers.append(
                            instance
                        )

                        loaded_provider_names.add(
                            instance.name
                        )

                        print()
                        print("# --------------------------------")
                        print("# PROVIDER LOADED")
                        print("# --------------------------------")
                        print(instance.name)
                        print("# --------------------------------")
                        print()

                except Exception as e:

                    print()
                    print("# --------------------------------")
                    print("# PROVIDER CREATE FAIL")
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
