import pandas as pd

# Define dictionaries
dictionaries = {
    'urgency_marketing': {
        'limited', 'limited time', 'limited run', 'limited edition', 'order now',
        'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
        'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
        'expires soon', 'final hours', 'almost gone'
    },
    'exclusive_marketing': {
        'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
        'members only', 'vip', 'special access', 'invitation only',
        'premium', 'privileged', 'limited access', 'select customers',
        'insider', 'private sale', 'early access'
    }
}

# Load data
df = pd.read_csv('sample_data.csv')

# Classification function
def classify_text(text, dictionary):
    if pd.isna(text):
        return 0
    text_lower = text.lower()
    return int(any(term in text_lower for term in dictionary))

# Apply classification
for dict_name, dict_terms in dictionaries.items():
    df[dict_name] = df['Statement'].apply(lambda x: classify_text(x, dict_terms))

# Save results
df.to_csv('classified_data.csv', index=False)
print("Classification complete!")
print(f"\nResults:\n{df[['Statement', 'urgency_marketing', 'exclusive_marketing']].head(10)}")