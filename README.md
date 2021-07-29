# Quick macros for Talon

This repository implements "quick macros" for Talon, which allows certain commands to automatically set a macro that can be invoked later. By default, it sets the popping noise to activate the current quick macro. It also overrides Talon's built in repeat_command action to temporarily set the quick macro to repeat the previous command. This means that whenever you repeat a command, if you want to repeat it further you can just pop.

You can also use quick macros in more sophisticated ways. For example, I have it set up so that whenever I perform a search, the quick macro is set to find the next match, so I can pop to quickly scan through the matches. You can see some further examples in example.talon.ignore.
