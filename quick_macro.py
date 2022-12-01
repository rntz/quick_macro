from talon import Module, actions, noise, ui, speech_system
from typing import Any, Optional
import logging
from dataclasses import dataclass

mod = Module()

setting_quick_macro_duration = mod.setting(
    "quick_macro_duration",
    type=int,
    default=10,
    desc="The default number of phrases after which a quick macro expires. -1 means never."
)

@dataclass
class QuickMacro:
    # the path to an action, eg. "user.paste"
    action: str
    # the arguments to pass, eg. ["hello world"]
    args: list
    # how many phrases before the macro expires. None means never.
    duration: Optional[int]
    # number of phrases since the macro was last set or invoked
    elapsed: int
    # whether to preserve the quick macro across window focus switches
    sticky: bool

quick_macro: Optional[QuickMacro] = None

@mod.action_class
class Actions:
    def quick_key(key: str):
        """Presses a key and makes it the quick macro."""
        actions.key(key)
        actions.user.quick_macro_set("key", key)

    def quick_key_transient(key: str):
        """Presses a key and makes it a transient quick macro."""
        actions.key(key)
        actions.user.quick_macro_transient("key", key)

    def quick_macro_clear():
        """Clears the quick macro"""
        global quick_macro
        # logging.info("Quick macro cleared")
        quick_macro = None

    def quick_macro_expiring(duration: Optional[int], action: str, arg: Any = None, sticky: bool = False):
        """Sets a quick macro which expires after a certain number of phrases"""
        global quick_macro
        if duration is None: duration = setting_quick_macro_duration.get()
        if duration < 0: duration = None # ie. never
        if duration == 0:
            logging.info("Quick macro with duration 0 expired immediately")
            return # okay, boss
        args = [arg] if arg is not None else []
        quick_macro = QuickMacro(
            action=action,
            args=args,
            duration=duration,
            elapsed=0,
            sticky=sticky)
        # logging.info(f"Quick macro set to {quick_macro!r}")

    def quick_macro_active() -> bool:
        """Returns true if a quick macro is currently active."""
        return quick_macro is not None

    def quick_macro_set(action: str, arg: Any = None):
        """Sets a quick macro"""
        actions.user.quick_macro_expiring(None, action, arg)

    def quick_macro_transient(action: str, arg: Any = None):
        """Sets a quick macro that expires after a single phrase"""
        actions.user.quick_macro_expiring(1, action, arg)

    def quick_macro_sticky(action: str, arg: Any = None):
        """Sets a quick macro that persists across focus changes"""
        actions.user.quick_macro_expiring(None, action, arg, sticky=True)

    def quick_macro_sticky_transient(action: str, arg: Any = None):
        """Sets a quick macro that persists across focus changes but expires after a single phrase"""
        actions.user.quick_macro_expiring(1, action, arg, sticky=True)

    def quick_macro_run():
        """Runs the quick macro"""
        global quick_macro
        macro = quick_macro
        if macro is None:
            logging.info("Quick macro invoked, but no quick macro assigned")
            return
        # logging.info(f"Quick macro invoked: {macro!r}")
        assert isinstance(macro, QuickMacro)
        func = actions
        for pathelt in macro.action.split('.'):
            func = getattr(func, pathelt)
        func(*macro.args)
        # In case invoking the quick macro set it to something else, we restore
        # it. This can happen eg. with regular macros. We also reset elapsed to
        # 0 to keep the quick macro active.
        # if macro != quick_macro:
        #     logging.info(f"Restored quick macro to {macro!r}, was {quick_macro!r}")
        quick_macro = macro
        macro.elapsed = 0

def on_focus_change():
    if not quick_macro or quick_macro.sticky: return
    # logging.info(f"Quick macro cleared by focus change, was {quick_macro!r}")
    actions.user.quick_macro_clear()

ui.register("app_deactivate", lambda app: on_focus_change())
ui.register("win_focus", lambda win: on_focus_change())

def on_phrase(j):
    global quick_macro
    # skip things that didn't get recognized
    if quick_macro is None or 'text' not in j: return
    quick_macro.elapsed += 1
    if quick_macro.duration is not None and quick_macro.elapsed >= quick_macro.duration:
        # logging.info(f"Quick macro expired, duration {quick_macro.duration}")
        actions.user.quick_macro_clear()

speech_system.register("phrase", on_phrase)
