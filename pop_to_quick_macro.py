# This causes popping to run the quick macro. Rename this file to something like
# pop_to_quick_macro.py.ignore to avoid this behavior, or just comment out the
# whole file.
from talon import noise, actions, scope
def on_pop(active):
    modes = scope.get("mode")
    if "sleep" not in modes:
        actions.user.quick_macro_run()
noise.register("pop", on_pop)
