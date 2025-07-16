import string
import re
from collections import Counter

# Load dictionary from system or fallback file
def load_dictionary(path="/usr/share/dict/words"):
    try:
        with open(path) as f:
            return set(word.strip().lower() for word in f if word.strip().isalpha())
    except FileNotFoundError:
        print("⚠️ Dictionary not found. Defaulting to a mini word list.")
        return {"the", "and", "hello", "world", "test", "this", "example", "python"}

# Caesar shift decryption
def caesar_decrypt(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)

# English frequency table (approximate)
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.49,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
    'Z': 0.07
}

def letter_frequency_score(text):
    text = re.sub(r'[^a-zA-Z]', '', text).upper()
    if not text:
        return 0.0
    total = len(text)
    counts = Counter(text)
    score = 0.0
    for letter, expected in ENGLISH_FREQ.items():
        actual = (counts.get(letter, 0) / total) * 100
        score += (100 - abs(actual - expected))  # closer = better
    return score

def evaluate_decryption(text, dictionary):
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())  # only valid words
    match_count = sum(1 for word in words if word in dictionary)
    freq_score = letter_frequency_score(text)
    total_score = match_count * 10 + freq_score
    return match_count, freq_score, total_score

def solve_caesar(ciphertext, dictionary):
    results = []
    normalized_input = re.sub(r'\s+', '', ciphertext.lower())

    for shift in range(-26, 27):
        if shift == 0:
            continue

        decoded = caesar_decrypt(ciphertext, shift)
        normalized_output = re.sub(r'\s+', '', decoded.lower())

        # Don't include original message
        if normalized_output == normalized_input:
            continue

        matches, freq_score, total_score = evaluate_decryption(decoded, dictionary)

        results.append({
            'shift': shift,
            'text': decoded,
            'matches': matches,
            'freq_score': freq_score,
            'total_score': total_score
        })

    results.sort(key=lambda x: x['total_score'], reverse=True)

    best = results[0]
    print(f"\n🔍 Best candidate (Shift={best['shift']}):")
    print(best['text'])
    print(f"Word Matches: {best['matches']} | Freq Score: {best['freq_score']:.1f} | Total Score: {best['total_score']:.1f}")

    print("\n📋==Best Canidates==")
    for r in results[:5]:
        dir_str = f"+{r['shift']}" if r['shift'] > 0 else str(r['shift'])
        preview = r['text'][:60].replace('\n', ' ')
        print(f"[Shift {dir_str:>3}] Score: {r['total_score']:6.1f} | Matches: {r['matches']:2} | {preview}")

# === MAIN ===
if __name__ == "__main__":
    ciphertext = input("Enter Caesar-encrypted text: ").strip()
    dictionary = load_dictionary()
    solve_caesar(ciphertext, dictionary)
