import pkgutil
import inspect
import importlib

from app.ai.providers.base import \
    AIProvider


class ProviderLoader:

    def load_all(self):

        providers = []

        package = (
            "app.ai.providers"
        )

        for module_info in (
            pkgutil.iter_modules(
                [
                    "/opt/MyAI/app/ai/providers"
                ]
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

                print(
                    f"[PROVIDER LOAD FAIL] "
                    f"{module_name}"
                )
                print(e)

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

                        providers.append(
                            obj()
                        )

                except Exception:
                    pass

        return providers
