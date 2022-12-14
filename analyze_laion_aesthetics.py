import datasets
from datasets import load_dataset
import numpy as np
import pandas as pd
from pathlib import Path
import os

dataset_path = 'ChristophSchuhmann/improved_aesthetics_5plus'
datasets.config.DOWNLOADED_DATASETS_PATH = Path('datasets')

characters = [
    ['Α', 'Greek Capital Letter Alpha', 'U+0391'],
    ['α', 'Greek Small Letter Alpha', 'U+03B1'],
    ['Β', 'Greek Capital Letter Beta', 'U+0392'],
    ['ο', 'Greek Small Letter Omicron', 'U+03BF'],
    ['Υ', 'Greek Capital Letter Upsilon', 'U+03A5'],
    ['Ν', 'Greek Capital Letter Nu', 'U+039D'],
    ['а', 'Cyrillic Small Letter A', 'U+0430'],
    ['А', 'Cyrillic A', 'U+0410'],
    ['В', 'Cyrillic B', 'U+0412'],
    ['О', 'Cyrillic O', 'U+041E'],
    ['е', 'Cyrillic Small Letter Ie', 'U+0435'],
    ['Å', 'Latin Capital Letter a with Ring Above', 'U+00C5'],
    ['å', 'Latin Small Letter a with Ring Above', 'U+00E5'],
    ['୦', 'Oriya digit zero', 'U+0B66'],
    ['ଠ', 'Oriya Letter Ttha', 'U+0B20'],
    ['𐒆', 'Osmanya Letter Deel', 'U+10486'],
    ['𐒃', 'Osmanya Letter Ja', 'U+10483'],
    ['𐒖', 'Osmanya Letter A', 'U+10496'],
    ['𐒋', 'Osmanya Letter Cayn', 'U+1048B'],
    ['ọ', 'Latin Small Letter O with Dot Below (Vietnamese)', 'U+1ECD'],
    ['ߋ', 'Nko Letter Ee', 'U+07CB'],
    ['ㅇ', 'Hangul Letter Ieung', 'U+3147'],
    ['।', 'Devanagari Danda', 'U+0964'],
    ['ꓲ', 'Lisu Letter I', 'U+A4F2'],
    ['།', 'Tibetan Mark Shad', 'U+0F0D'],
    ['á', 'Latin Small Letter a with Acute', 'U+00E1'],
    ['à', 'Latin Small Letter a with Grave', 'U+00E0'],
    ['â', 'Latin Small Letter a with Circumflex', 'U+00E2'],
    ['ã', 'Latin Small Letter a with Tilde', 'U+00E3'],
    ['ａ', 'Fullwidth Latin Small Letter A', 'U+FF41'],
    ['😃', 'Smiling Face with Open Mouth Emoji', 'U+1F603'],
    ['🤬', 'Serious Face With Symbols Covering Mouth Emoji', 'U+1F92C'],
    ['😭', 'Loudly Crying Face Emoji', 'U+1F62D'],
    ['🥰', 'Smiling Face with Smiling Eyes and Three Hearts Emoji', 'U+1F970'],
    ['😱', 'Face Screaming In Fear Emoji', 'U+1F631'],
    ['🥳', 'Face with Party Horn and Party Hat Emoji', 'U+1F973'],
    ['🤓', 'Nerd Face Emoji', 'U+1F913'],
    ['🐵', 'Monkey Face Emoji', 'U+1F435'],
    ['🐫', 'Bactrian Camel Emoji', 'U+1F42B'],
    ['ا', 'Arabic Letter Alef', 'U+0627']
]

def main():
    # Download dataset files from hugging face
    dataset = load_dataset(dataset_path)

    # Analyze each file separately
    os.makedirs('laion_aestetics_results_per_file', exist_ok=True)
    num_files = len( os.listdir('datasets'))
    for j, file in enumerate(os.listdir('datasets')):
        file_path = os.path.join('datasets', file)

        if 'json' in file_path or 'lock' in file_path:
            continue

        if os.path.exists(f'laion_aestetics_results_per_file/{file}.csv'):
            print(f'File {file}.csv already existing')
            continue

        try:
            dataset = load_dataset("parquet", data_files=file_path)
            df = pd.DataFrame(dataset['train'])

            for i in range(len(characters)):
                print(f'current index: {i} of {len(characters)}')
                c = characters[i][0]
                df_filtered = df[df['TEXT'].str.contains(c, na=False)][['URL', 'TEXT']]
                characters[i].append(len(df_filtered))

            df_result = pd.DataFrame(characters)
            df_result.to_csv(f'laion_aestetics_results_per_file/{file}.csv')
            print(f'Analyzed file {j} of {num_files}')
        except Exception as e:
            print(f'Problem with {file_path}')

    # Merge results
    files = os.listdir('laion_aestetics_results_per_file')
    file_list = []
    for f in files:
        if len(f) > 20:
            df = pd.read_csv(os.path.join('laion_aestetics_results_per_file', f))
            file_list.append(df)

    df_final = file_list[0]
    for f in file_list[1:]:
        df_final['3'] += f['3']

    df_final[['1', '2', '3']].to_csv('dataset_analysis.csv')

if __name__ == "__main__":
    main()
