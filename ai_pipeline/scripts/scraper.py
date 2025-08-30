import requests
import json
import time
from bs4 import BeautifulSoup
import ast
import hashlib
import os
import sqlite3 as sqlite

DATABASE_PATH = "../schemas/code_snippets.db"
MAX_SNIPPETS_TO_FETCH_FROM_SOURCE = 1
MAX_RETRIES_PER_SOURCE = 10

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"] if "GITHUB_TOKEN" in os.environ else None

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

CATEGORY_KEYWORDS = {
    "Algorithms/Logic": ["recursion", "algorithm", "loop", "sort"],
    "Machine Learning": ["pytorch", "tensorflow", "sklearn", "training"],
    "Web/API Code": ["flask", "fastapi", "django", "request"],
    "Data Processing": ["pandas", "numpy", "csv", "json"],
}

output_data = []
hash_set = set()

conn = None
cursor = None

def main():
    connect_to_db()

    for label, keywords in CATEGORY_KEYWORDS.items():
        print(f"\n=== Collecting for: {label} ===")

        for tag in keywords:
            try:
                fetch_stackoverflow_code(tag, label, MAX_SNIPPETS_TO_FETCH_FROM_SOURCE)
            except Exception as e:
                print(f"StackOverflow error for tag {tag}: {e}")

            if not GITHUB_TOKEN:
                print("Skipping GitHub fetch (no token)")
                continue

            try:
                fetch_github_code(tag, label, MAX_SNIPPETS_TO_FETCH_FROM_SOURCE)
            except Exception as e:
                print(f"GitHub error for keyword {tag}: {e}")
    

def connect_to_db():
    global conn, cursor
    conn = sqlite.connect(DATABASE_PATH)
    cursor = conn.cursor()

def get_current_data():
    current_data = []
    codes_in_current = set()
    try:
        with open("code_dataset.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
            codes_in_current = {item["code"] for item in current_data}
    except Exception:
        pass

    return current_data, codes_in_current

def update_current_data(new_data, current_data, codes_in_current):
    for item in new_data:
        if item["code"] not in codes_in_current:
            current_data.append(item)

def write_to_output(data):
    with open("code_dataset.json", "w", encoding="utf-8") as f:    
        json.dump(data, f)

def fetch_stackoverflow_code(tag, label, max_snippets=50):
    print(f"[StackOverflow] Scraping tag: {tag}")
    page = 1
    collected = 0
    attempts = 0

    while collected < max_snippets and attempts < MAX_RETRIES_PER_SOURCE:
        url = f"https://stackoverflow.com/questions/tagged/{tag}?tab=newest&page={page}"
        resp = requests.get(url, timeout=10)
        attempts += 1
        
        if resp.status_code != 200:
            print(f"StackOverflow error: {resp.status_code}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        questions = soup.select(".s-post-summary--content-title a")

        for q in questions:
            q_url = "https://stackoverflow.com" + q["href"]

            if query_url_in_db(q_url):
                continue

            q_html = requests.get(q_url, timeout=10).text
            q_soup = BeautifulSoup(q_html, "html.parser")

            code_blocks = q_soup.select("pre code")
            for code_tag in code_blocks:
                code = code_tag.get_text()

                snippets_added = add_valid_snippets_from_tag(code, label, "stackoverflow", q_url)
                
                if snippets_added:
                    print("Added snippet from StackOverflow")
                    collected += 1
                    if collected >= max_snippets:
                        return
            
            time.sleep(3)
                            
        page += 1
        time.sleep(3)

def query_url_in_db(url):
    cursor.execute("SELECT 1 FROM snippets WHERE url = ?", (url,))
    return cursor.fetchone() is not None

def add_valid_snippets_from_tag(code, label, source_name, source_url):
    for snippet in extract_ast_snippets(code):
        normalized_snippet = normalize_code(snippet)

        if snippet_is_valid(normalized_snippet):
            added = add_snippet(normalized_snippet, label, source_name, source_url)

            if added:
                return True

    return False

def fetch_github_code(keyword, label, max_snippets=50):
    print(f"[GitHub] Searching: {keyword}")
    collected = 0
    page = 1
    attempts = 0

    while collected < max_snippets and attempts < MAX_RETRIES_PER_SOURCE:
        url = f"https://api.github.com/search/code?q={keyword}+language:python&per_page=30&page={page}"
        print(" Searching page")
        r = requests.get(url, headers=HEADERS, timeout=10)
        attempts += 1

        if r.status_code != 200:
            print(f"GitHub API error: {r.status_code}")
            break

        items = r.json().get("items", [])
        for item in items:
            raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
            if query_url_in_db(raw_url):
                continue

            raw_code = requests.get(raw_url, timeout=10)
            
            if raw_code.status_code != 200:
                print("Failed to fetch raw code")
                continue

            snippets_added = add_valid_snippets_from_tag(raw_code.text, label, "github", raw_url)
                
            if snippets_added:
                print("Added snippet from Github")
                collected += 1
                if collected >= max_snippets:
                    return
            
            time.sleep(3)

        page += 1
        time.sleep(3)

def extract_ast_snippets(code):
    try:
        parsed = ast.parse(code)
        snippets = []
        for node in parsed.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                snippet = ast.unparse(node) if hasattr(ast, "unparse") else ast.dump(node)
                snippets.append(snippet)
        return snippets
    except Exception:
        return []

def deduplicate_and_add(code, label):
    """Add to output if not a duplicate and valid"""
    code = normalize_code(code)
    if 20 < len(code) < 1000:  # filter out trivial or overly long
        h = code_hash(code)
        if h not in hash_set:
            hash_set.add(h)
            output_data.append({"code": code, "label": label})

def normalize_code(code):
    """Minify and normalize code for deduplication"""
    return '\n'.join(line.strip() for line in code.strip().splitlines() if line.strip())

def snippet_is_valid(code):
    return 20 < len(code) < 1000

def add_snippet(code, label, source, url):
    h = code_hash(code)

    try:
        cursor.execute("INSERT INTO snippets (code, source, url, label, hash) VALUES (?, ?, ?, ?, ?)",
                    (code, source, url, label, h))
        conn.commit()
    except sqlite.IntegrityError:
        return False

    return True

    if h not in hash_set:
        hash_set.add(h)
        output_data.append({"code": code, "label": label})
        return True
    
    return False

def code_hash(code):
    return hashlib.md5(normalize_code(code).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    main()
