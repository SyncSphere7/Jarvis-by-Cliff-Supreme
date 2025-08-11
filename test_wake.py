from core.voice.wakeword import detect_wakeword

print("== Wake Word Test ==")
print("1. Say just 'Jarvis' (should detect)")
print("2. Say 'Hey Jarvis' (should ignore)")
print("3. Say other words (should ignore)")

while True:
    input("Press Enter to test (Ctrl+C to quit)...")
    if detect_wakeword():
        print(">> Wake word DETECTED")
    else:
        print(">> No wake word")
