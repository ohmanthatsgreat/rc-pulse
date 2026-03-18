# RC Pulse Demo
Output demo/rc-pulse-demo.mp4
Output demo/rc-pulse-demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1100
Set Height 750
Set Padding 15
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms
Set PlaybackSpeed 1

Sleep 1s

# Intro
Type "# RC Pulse — AI-Powered Subscription Health Reports"
Enter
Type "# Built by Cleo Sterling (AI) | RevenueCat Charts API"
Enter
Sleep 3s

Type "clear"
Enter
Sleep 500ms

# Show the command we're about to run
Type "# Let's generate a health report for the Dark Noise app"
Enter
Sleep 2s
Type "python3 -m rc_pulse.cli report --api-key $RC_API_KEY --start 2025-01-01 --end 2026-03-18"
Enter

# Wait for output (using replay script for speed)
Sleep 15s

# Pause on the results
Sleep 10s

Type ""
Enter
Sleep 1s

# Show HTML option
Type "# Now let's export as an HTML dashboard"
Enter
Sleep 1.5s
Type "python3 -m rc_pulse.cli report --api-key $RC_API_KEY --start 2025-01-01 --end 2026-03-18 --format html -o pulse-report.html"
Enter
Sleep 15s

Sleep 3s

Type ""
Enter
Type "# Also supports: --format markdown, --format json"
Enter
Sleep 2s
Type "# pip install rc-pulse | github.com/ohmanthatsgreat/rc-pulse"
Enter
Sleep 5s
