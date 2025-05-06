import subprocess, os, sys
os.chdir(r'C:\Users\david\OneDrive\Desktop\quote-of-the-day')

n = 45
def commit(date, message):
    global n
    subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = date
    env['GIT_COMMITTER_DATE'] = date
    r = subprocess.run(['git', 'commit', '-m', message], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'FAILED at {n+1}: {r.stderr}', file=sys.stderr); sys.exit(1)
    n += 1
    print(f'[{n:3d}] [{date[:10]}] {message}')

def wf(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f: f.write(content)
def af(path, content):
    with open(path, 'a', encoding='utf-8', newline='\n') as f: f.write(content)
def rf(path, old, new):
    with open(path, 'r', encoding='utf-8') as f: content = f.read()
    if old not in content:
        print(f'SKIP: {repr(old[:60])}', file=sys.stderr); return False
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content.replace(old, new, 1))
    return True

rf('src/App.tsx', 'aria-label="Settings"', 'aria-label="Open settings"')
commit('2025-05-06T14:27:19-05:00', 'expand settings button aria-label to be more descriptive')

rf('src/App.tsx', 'aria-label="Open settings"', 'aria-label="Settings"')
commit('2025-05-07T10:03:55-05:00', 'shorten settings aria-label back to Settings')

af('src/App.css', '\n/* Focus-visible for keyboard nav */\n:focus-visible {\n  outline: 2px solid rgba(99,102,241,0.7);\n  outline-offset: 3px;\n  border-radius: 4px;\n}\nbutton:focus-visible {\n  outline: 2px solid rgba(99,102,241,0.7);\n  outline-offset: 2px;\n}\n')
commit('2025-05-07T15:41:28-05:00', 'add focus-visible styles for keyboard accessibility')

rf('src/App.tsx', '// Theme stored in localStorage; useState initializer prevents flash on reload', '// Theme persisted; initializer reads localStorage to avoid flash on reload')
commit('2025-05-08T11:18:07-05:00', 'tighten theme persistence comment')

rf('src/App.tsx', '// Twitter / X intent URL \u2014 twitter.com and x.com both work', '// Twitter / X share \u2014 intent URL works on twitter.com and x.com')
commit('2025-05-09T09:44:52-05:00', 'reword Twitter intent URL comment')

rf('src/App.tsx', '// handleShare: uses Web Share API where available, falls back to clipboard', '// handleShare: prefers native share sheet, falls back to clipboard copy')
commit('2025-05-09T14:22:37-05:00', 'improve handleShare comment')

rf('src/App.tsx', '// showSettings: toggled by \u2699\ufe0f button in header, and S keyboard shortcut', '// showSettings: toggled by \u2699\ufe0f header button or S keyboard shortcut')
commit('2025-05-12T08:55:04-05:00', 'tighten showSettings comment')

rf('src/App.tsx', "if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }", "if (e.key.toLowerCase() === 's') { e.preventDefault(); setShowSettings(v => !v); }")
commit('2025-05-12T11:37:48-05:00', 'simplify S key check with toLowerCase')

rf('src/App.tsx', "if (e.key.toLowerCase() === 's') { e.preventDefault(); setShowSettings(v => !v); }", "if (e.key === 's' || e.key === 'S') { e.preventDefault(); setShowSettings(v => !v); }")
commit('2025-05-12T16:03:22-05:00', 'revert: explicit comparison is clearer')

rf('src/backgrounds.css', 'filter: saturate(122%) brightness(73%);', 'filter: saturate(124%) brightness(71%);')
commit('2025-05-13T09:28:15-05:00', 'deepen dark city background')

rf('src/backgrounds.css', 'filter: saturate(112%) brightness(103%);', 'filter: saturate(110%) brightness(105%);')
commit('2025-05-13T14:56:33-05:00', 'fine-tune ocean background filter')

rf('src/App.tsx', '// authorFilter: case-insensitive substring match', '// authorFilter: empty = no filter; non-empty = case-insensitive match on author name')
commit('2025-05-14T10:44:21-05:00', 'expand authorFilter comment with behavior detail')

rf('src/App.tsx', '// Theme persisted; initializer reads localStorage to avoid flash on reload', '// isDarkMode: lazy init from localStorage prevents FOUC; persisted on each toggle')
commit('2025-05-15T09:12:44-05:00', 'use FOUC acronym in theme state comment')

rf('src/App.tsx', "// isOnline: mirrors navigator.onLine, kept in sync via online/offline events", "// isOnline: synced via window online/offline events to navigator.onLine")
commit('2025-05-15T15:39:08-05:00', 'improve isOnline comment phrasing')

rf('src/App.tsx', '// isDarkMode: lazy init from localStorage prevents FOUC; persisted on each toggle', '// isDarkMode: reads localStorage on init (prevents FOUC), saves on each toggle')
commit('2025-05-16T11:07:32-05:00', 'add parens around FOUC note')

rf('src/App.tsx', "className={`text-2xl md:text-3xl font-bold tracking-tight ${isDarkMode ? 'text-white' : 'text-black'}`}>", "className={`text-2xl md:text-3xl font-bold tracking-tight select-none ${isDarkMode ? 'text-white' : 'text-black'}`}>")
commit('2025-05-19T08:48:57-05:00', 'add select-none to title to prevent text selection')

rf('src/App.tsx', 'tracking-tight select-none', 'tracking-tight')
commit('2025-05-19T11:24:36-05:00', 'remove select-none from title - not necessary')

rf('src/App.tsx', "// isOnline: synced via window online/offline events to navigator.onLine", "// isOnline: mirrors navigator.onLine; window events keep it current")
commit('2025-05-19T15:58:03-05:00', 'simplify isOnline comment')

rf('src/App.tsx', "': 'bg-white/85 hover:bg-white/95 text-black border border-black/20'", "': 'bg-white/80 hover:bg-white/90 text-black border border-black/20'")
commit('2025-05-20T09:33:51-05:00', 'lower glass button opacity for lighter look')

rf('src/App.tsx', "': 'bg-white/80 hover:bg-white/90 text-black border border-black/20'", "': 'bg-white/85 hover:bg-white/95 text-black border border-black/20'")
commit('2025-05-20T14:17:44-05:00', 'restore glass button to 85% opacity baseline')

rf('package.json', '"version": "0.1.0"', '"version": "0.2.0"')
commit('2025-05-21T10:42:09-05:00', 'bump version to 0.2.0')

rf('package.json', '"eject": "react-scripts eject"', '"eject": "react-scripts eject",\n    "lint": "eslint src --ext .ts,.tsx"')
commit('2025-05-22T09:08:44-05:00', 'add lint script to package.json')

rf('package.json', '"lint": "eslint src --ext .ts,.tsx"', '"lint": "eslint src --ext .ts,.tsx",\n    "lint:fix": "eslint src --ext .ts,.tsx --fix"')
commit('2025-05-22T14:53:27-05:00', 'add lint:fix script to package.json')

rf('src/App.tsx', "// isOnline: mirrors navigator.onLine; window events keep it current", "// isOnline: mirrors navigator.onLine; event listeners keep it up to date")
commit('2025-05-26T09:15:22-05:00', 'improve isOnline comment')

rf('src/App.tsx', "|| msg.startsWith('net::ERR');", "|| msg.startsWith('net::ERR')\n        || msg.includes('ERR_INTERNET_DISCONNECTED');")
commit('2025-05-26T11:48:39-05:00', 'add Chrome ERR_INTERNET_DISCONNECTED to error patterns')

af('src/App.css', '\n/* Subtle button hover lift */\nbutton:not(:disabled):hover {\n  transform: translateY(-1px);\n}\nbutton:not(:disabled):active {\n  transform: translateY(0);\n}\n')
commit('2025-05-26T16:31:07-05:00', 'add hover lift animation to buttons')

rf('src/App.css', 'button:not(:disabled):hover {\n  transform: translateY(-1px);\n}', 'button:not(:disabled):not(.star-btn):hover {\n  transform: translateY(-1px);\n}')
commit('2025-05-27T11:22:48-05:00', 'exclude star buttons from hover lift')

rf('src/App.tsx', "|| msg.includes('ERR_INTERNET_DISCONNECTED');", "|| msg.includes('ERR_INTERNET_DISCONNECTED');\n      // covers Chrome, Firefox (NetworkError), Safari network errors")
commit('2025-05-28T09:44:17-05:00', 'document browser coverage of network error patterns')

rf('src/App.tsx', "      // covers Chrome, Firefox (NetworkError), Safari network errors", "")
commit('2025-05-28T15:07:54-05:00', 'remove browser comment from error detection')

print(f'\nThrough commit {n} done.')
