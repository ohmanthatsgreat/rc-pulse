# RC Pulse Demo — Fast replay version
Output demo/rc-pulse-demo.mp4
Output demo/rc-pulse-demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1100
Set Height 700
Set Padding 15
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms

Sleep 500ms
Type "# RC Pulse — AI-Powered Subscription Health Reports"
Enter
Type "# from RevenueCat's Charts API"
Enter
Sleep 2s

Type "clear"
Enter
Sleep 500ms

# Show what we're about to do
Type "cat README.md | head -20"
Enter
Sleep 4s

Type "clear"
Enter
Sleep 500ms

# Run the actual tool with pre-cached output
Type "python3 -m rc_pulse.cli report --api-key $RC_API_KEY --start 2025-01-01 --end 2026-03-18"
Enter
Sleep 180s

Sleep 8s

Type "clear"
Enter
Sleep 500ms

# Show markdown format
Type "python3 -m rc_pulse.cli report --api-key $RC_API_KEY --start 2025-01-01 --end 2026-03-18 --format markdown | head -40"
Enter
Sleep 180s

Sleep 6s

Type ""
Enter
Type "# Full repo: github.com/ohmanthatsgreat/rc-pulse"
Enter
Type "# Built by Cleo Sterling — an AI agent 🤖"
Enter
Sleep 5s
