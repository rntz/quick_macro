from talon import Module, actions, noise, ui, speech_system
from typing import Any, Optional
import logging

mod = Module()

setting_quick_macro_duration = mod.setting(
    "quick_macro_duration",
    type=int,
    default=10,
    desc="The default number of phrases after which a quick macro expires. -1 means never."
)

# quick_macro may be None or a tuple (action, args...).
# None: no quick macro assigned.
# (action, args...)
#   `action` is the path to an action.
#   `args` are the arguments to the action.
quick_macro = None

# how many phrases before the macro expires
quick_macro_expires = None

# number of phrases since the macro was last set or invoked
quick_macro_elapsed = 0

@mod.action_class
class Actions:
    def quick_macro_clear():
        """Clears the quick macro"""
        global quick_macro, quick_macro_expires
        logging.info("== Quick macro cleared ==")
        quick_macro = None
        quick_macro_expires = None

    def quick_macro_expiring(expires: Optional[int], action: str, arg: Any = None):
        """Sets a quick macro which expires after a certain number of phrases"""
        global quick_macro, quick_macro_expires, quick_macro_elapsed
        if expires is None: expires = setting_quick_macro_duration.get()
        if expires <= 0: expires = None # ie. never
        quick_macro = (action, arg) if arg is not None else (action,)
        quick_macro_expires = expires
        quick_macro_elapsed = 0
        logging.info(f"== Quick macro set to {quick_macro!r}, duration {quick_macro_expires!r} ==")

    def quick_macro_set(action: str, arg: Any = None):
        """Sets a quick macro"""
        actions.user.quick_macro_expiring(None, action, arg)

    def quick_macro_transient(action: str, arg: Any = None):
        """Sets a quick macro that expires after a single phrase"""
        actions.user.quick_macro_expiring(1, action, arg)

    def quick_macro_run():
        """Runs the quick macro"""
        if not isinstance(quick_macro, tuple):
            if quick_macro is None:
                logging.info("== Quick macro invoked, but no quick macro assigned ==")
            else:
                logging.warn(f"== Unknown quick macro invoked: {quick_macro!r} ==")
            return
        logging.info(f"== Quick macro invoked: {quick_macro!r} ==")
        action, *args = quick_macro
        func = actions
        for pathelt in action.split('.'):
            func = getattr(func, pathelt)
        func(*args)
        # we do this after invoking the action in case it causes the elapsed
        # counter to increase somehow
        global quick_macro_elapsed
        quick_macro_elapsed = 0

ui.register("app_deactivate", lambda app: actions.user.quick_macro_clear())
ui.register("win_focus", lambda win: actions.user.quick_macro_clear())

def on_phrase(j):
    global quick_macro_elapsed
    # skip things that didn't get recognized
    if 'text' not in j: return
    if quick_macro_expires is not None:
        logging.info(f"== ELAPSED {quick_macro_elapsed}, EXPIRES {quick_macro_expires} ==")
    quick_macro_elapsed += 1
    if quick_macro_expires is not None and quick_macro_elapsed >= quick_macro_expires:
        logging.info(f"== QUICK MACRO EXPIRED, {quick_macro_expires} ==")
        actions.user.quick_macro_clear()
speech_system.register("phrase", on_phrase)
