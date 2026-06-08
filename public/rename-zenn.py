import os
import re
import glob
import yaml
from deep_translator import GoogleTranslator

def has_japanese(text):
    return bool(re.search(r'[^\x00-\x7F]', text))

def to_snake_case(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    return text

def convert_zenn_to_qiita():
    translator = GoogleTranslator(source='ja', target='en')
    
    for filepath in glob.glob("*.md"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                continue
                
            zenn_matter = yaml.safe_load(match.group(1))
            body = content[match.end():]
            
            title = zenn_matter.get('title', '')
            if not title:
                continue
            
            if has_japanese(title):
                english_title = translator.translate(title)
            else:
                english_title = title
                
            if not english_title:
                print(f"Failed to translate title for: {filepath}")
                continue
                
            safe_name = to_snake_case(english_title)
            new_filename = f"{safe_name}.md"
            
            qiita_matter = {
                'title': title,
                'tags': zenn_matter.get('topics', []),
                'private': False,
                'updated_at': zenn_matter.get('published_at', ''),
                'id': None,
                'organization_url_name': None,
                'slide': False
            }
            
            new_front_matter_text = yaml.dump(qiita_matter, allow_unicode=True, sort_keys=False)
            new_content = f"---\n{new_front_matter_text}---\n{body}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            if filepath != new_filename:
                os.rename(filepath, new_filename)
                print(f"Processed & Renamed: {filepath} -> {new_filename}")
            else:
                print(f"Processed: {filepath}")
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    convert_zenn_to_qiita()
