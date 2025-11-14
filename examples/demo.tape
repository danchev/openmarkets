# Source code for the VHS demo example.
#
# To run:
#
#     vhs < demo.tape

Output demo.gif
Output demo.mp4
Output demo.webm
Output frames/
Output demo.gif

Set CursorBlink false
Set PlaybackSpeed 2.0
Set TypingSpeed 75ms
Set FontSize 18
Set Width 1300
Set Height 650

Hide
Type 'openmarkets() { crush run -q "$@" | glow; } && clear'
Enter
Show

Type@100ms "openmarkets 'Generate a comprehensive technical market report for Alphabet Inc. (ticker: GOOG)'"

Sleep 500ms

Enter

Sleep 30s
