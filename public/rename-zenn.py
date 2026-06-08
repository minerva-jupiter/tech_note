
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

def rename_zenn_articles():
    translator = GoogleTranslator(source='ja', target='en')
    
    for filepath in glob.glob("*.md"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # フロントマターの抽出
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                continue
                
            front_matter = yaml.safe_load(match.group(1))
            title = front_matter.get('title')
            
            if not title:
                continue
            
            # 翻訳処理
            if has_japanese(title):
                english_title = translator.translate(title)
            else:
                english_title = title
                
            if not english_title:
                print(f"Failed to translate: {title}")
                continue
                
            # スネークケース変換とリネーム
            safe_name = to_snake_case(english_title)
            new_filename = f"{safe_name}.md"
            
            if filepath != new_filename:
                os.rename(filepath, new_filename)
                print(f"Renamed: {filepath} -> {new_filename}")
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    rename_zenn_articles()
