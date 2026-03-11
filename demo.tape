# peasy-image — Python Image Toolkit Demo
Output demo.gif

Set FontSize 20
Set Width 1000
Set Height 580
Set Shell "zsh"
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Padding 24

Type "uv run --with peasy-image python3"
Enter
Sleep 2.5s

Type "from peasy_image import info, resize, convert, compress"
Enter
Sleep 1s

Type "# Get image dimensions and metadata"
Enter
Sleep 0.5s

Type "i = info('/tmp/sample.png')"
Enter
Sleep 1.5s

Type "print(f'{i.width}x{i.height} {i.format} — {i.file_size/1024:.0f} KB')"
Enter
Sleep 1.5s

Type "# Resize to 400px wide (aspect ratio preserved)"
Enter
Sleep 0.5s

Type "resized = resize('/tmp/sample.png', width=400)"
Enter
Sleep 1.5s

Type "print(f'Resized: {len(resized)/1024:.0f} KB')"
Enter
Sleep 1.5s

Type "# Convert PNG to WebP"
Enter
Sleep 0.5s

Type "webp = convert('/tmp/sample.png', fmt='webp')"
Enter
Sleep 1.5s

Type "print(f'WebP: {len(webp)/1024:.0f} KB')"
Enter
Sleep 1.5s

Type "exit()"
Enter
Sleep 1s
