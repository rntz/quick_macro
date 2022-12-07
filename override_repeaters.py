# This overrides all commands that repeat actions to transiently set the quick
# macro to repeat the last action. Rename this file to something like
# override_repeaters.py.ignore to avoid this behavior, or just comment out the
# whole file.
from talon import Module, Context, actions
ctx = Context()
@ctx.action_class("core")
class override_repeaters:
    def repeat_command(times = 1):
        # Clear the quick macro, then run the command. If it sets a quick macro
        # we preserve it, otherwise we make a transient quick macro that repeats
        # the command.
        actions.user.quick_macro_clear()
        actions.next(times)
        if not actions.user.quick_macro_active():
            actions.user.quick_repeat()
