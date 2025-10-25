# Videos Directory

This directory is for your **local test videos**.

## 📁 How it works

- **Drop videos here**: Place your gaming footage in this directory
- **Already gitignored**: All video files (`.mp4`, `.mov`, `.mkv`, etc.) are automatically excluded from git
- **Never committed**: Your videos stay local and private - they're never pushed to GitHub
- **Any size welcome**: Store 5GB+ files without worrying about repository size

## 🎮 Usage

```bash
# Place your video in this directory
cp ~/Desktop/my_gameplay.mp4 videos/

# Run the highlight extractor
gaming-highlights videos/my_gameplay.mp4
```

## 🔗 Sharing Test Videos

**Don't commit video files!** Instead, share links in issue comments:

- **Google Drive**: Upload and share a link
- **YouTube**: Upload as unlisted and share URL
- **Dropbox/OneDrive**: Share a download link

See `.gitignore` for the complete list of excluded video formats.

## 💡 Pro Tips

- Keep videos here for easy reference
- Use descriptive filenames: `apex_triple_kill.mp4`, `valorant_clutch_1v4.mp4`
- Large files (5GB+)? The tool will warn you and suggest extracting shorter segments
- Test with shorter clips first (1-2 minutes) to iterate faster
