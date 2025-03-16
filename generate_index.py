import os, glob, re
from datetime import datetime
import markdown

POSTS_DIR = '_posts'
OUTPUT_DIR = 'public'

print(f"DEBUG: Checking for Markdown files in {POSTS_DIR}...")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

posts = []

md_files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
print(f"DEBUG: Found {len(md_files)} Markdown files: {md_files}")

for filepath in md_files:
    print(f"DEBUG: Processing {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    front_matter = {}
    content_lines = []
    if lines and lines[0].strip() == '---':
        idx = 1
        while idx < len(lines) and lines[idx].strip() != '---':
            line = lines[idx]
            m = re.match(r'([^:]+):\s*(.*)', line)
            if m:
                key = m.group(1).strip().lower()
                value = m.group(2).strip().strip('"')
                front_matter[key] = value
            idx += 1
        # The actual content starts after the second '---'
        content_lines = lines[idx+1:]
    else:
        # If no triple-dash front matter, treat entire file as content
        print("DEBUG: No front matter found, using entire file as content.")
        content_lines = lines

    title = front_matter.get('title', 'No Title')
    date_str = front_matter.get('date', '1970-01-01')
    
    print(f"DEBUG: Extracted title={title}, date={date_str}")

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("DEBUG: Invalid date format, defaulting to 1970-01-01.")
        date_obj = datetime(1970, 1, 1)
    
    content_md = '\n'.join(content_lines)
    content_html = markdown.markdown(content_md)
    
    # Create a slug from the title
    slug = re.sub(r'\W+', '-', title.lower()).strip('-')
    output_filename = f"{date_str}-{slug}.html"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header><h1>{title}</h1></header>
  <p>Posted on {date_str}</p>
  <main>{content_html}</main>
  <footer>&copy; 2025 My Blog</footer>
</body>
</html>
"""
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"DEBUG: Wrote HTML to {output_filename}")

    posts.append({
        'title': title,
        'date': date_obj,
        'filename': output_filename
    })

# Sort posts by date
posts.sort(key=lambda x: x['date'])

print("DEBUG: Generating index.html with grouped posts by day...")
index_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My Blog</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>Welcome to My Blog</header>
  <main>
    <h2>Recent Posts</h2>
"""

current_date = None
for post in posts:
    date_formatted = post['date'].strftime('%Y-%m-%d')
    if date_formatted != current_date:
        index_content += f"<h3>{date_formatted}</h3>\n"
        current_date = date_formatted
    index_content += f"<a href='{post['filename']}'>{post['title']}</a><br>\n"

index_content += """
  </main>
  <footer>&copy; 2025 My Blog</footer>
</body>
</html>
"""

with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_content)

print("DEBUG: Finished generating index.html.")
