import torch
import clip
import open_clip
from multilingual_clip import pt_multilingual_clip
import transformers
from PIL import Image

import os
import numpy as np
import pandas as pd

# Define the image paths and prompts for the current analysis
img_paths = 'real_samples/banhbao'
output_file = 'banhbao_obfuscated'
files = os.listdir(img_paths)
device = "cuda" if torch.cuda.is_available() else "cpu"
output_folder = 'athens_results'

prompts = [
    'Banh bao on a plate',
    'Banh bao on a ꓑlate',
    'ꓐanh bao on a plate',
    'Banh ꓐao on a plate',
    'ꓐanh ꓐao on a plate',
    'ꓐanh ꓐao on a ꓑlate',
]


def clip_similarity(path, prompt, clip_model, clip_preprocess):
    img = Image.open(path)
    image = clip_preprocess(img).unsqueeze(0).to(device)
    text = clip.tokenize(prompt).to(device)

    with torch.no_grad():
        image_features = clip_model.encode_image(image)
        text_features = clip_model.encode_text(text)
        
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).detach()

    return similarity

def open_clip_similarity(path, prompt, clip_model, clip_preprocess):
    img = Image.open(path)
    image = clip_preprocess(img).unsqueeze(0).to(device)
    text = open_clip.tokenize(prompt).to(device)

    with torch.no_grad():
        image_features = clip_model.encode_image(image)
        text_features = clip_model.encode_text(text)
        
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).detach()
    return similarity


def Mclip_similarity(path, prompt, clip_model, clip_preprocess, clipM_model, tokenizer):
    img = Image.open(path)
    image = clip_preprocess(img).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = clip_model.encode_image(image).float().cpu()
        text_features = clipM_model.forward(prompt, tokenizer)
        
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).detach()
    return similarity

def main():
    os.makedirs(f'{output_folder}', exist_ok=True)

    clip_model_vit, clip_preprocess_vit = clip.load("ViT-B/32", device=device)
    clip_model_rn50, clip_preprocess_rn50 = clip.load("RN50", device=device)

    openclip, _, openclip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_e16')

    Mclip_model = pt_multilingual_clip.MultilingualCLIP.from_pretrained('M-CLIP/XLM-Roberta-Large-Vit-B-32')
    Mclip_tokenizer = transformers.AutoTokenizer.from_pretrained('M-CLIP/XLM-Roberta-Large-Vit-B-32')

    # CLIP ViT Results
    row_list = []
    for file in files:
        file_path = os.path.join(img_paths, file)
        sim_clip_vit = clip_similarity(file_path, prompts, clip_model_vit, clip_preprocess_vit)
        sim_clip_vit = np.array(sim_clip_vit.cpu().tolist()[0])
        row_list.append(sim_clip_vit)
    df_clip_vit = pd.DataFrame(row_list, columns=prompts)
    df_clip_vit.to_csv(f'{output_folder}/{output_file}_clip_vit.csv', index=False)

    # CLIP RN50 Results
    row_list = []
    for file in files:
        file_path = os.path.join(img_paths, file)
        sim_clip_vit = clip_similarity(file_path, prompts, clip_model_rn50, clip_preprocess_rn50)
        sim_clip_vit = np.array(sim_clip_vit.cpu().tolist()[0])
        row_list.append(sim_clip_vit)
    df_clip_vit = pd.DataFrame(row_list, columns=prompts)
    df_clip_vit.to_csv(f'{output_folder}/{output_file}_clip_rn50.csv', index=False)

    # CLIP OpenCLIP
    row_list = []
    for file in files:
        file_path = os.path.join(img_paths, file)
        sim_clip_vit = open_clip_similarity(file_path, prompts, openclip.cuda(), openclip_preprocess)
        sim_clip_vit = np.array(sim_clip_vit.cpu().tolist()[0])
        row_list.append(sim_clip_vit)
    df_clip_vit = pd.DataFrame(row_list, columns=prompts)
    df_clip_vit.to_csv(f'{output_folder}/{output_file}_openclip.csv', index=False)

    # MCLIP
    row_list = []
    for file in files:
        file_path = os.path.join(img_paths, file)
        sim_clip_vit = Mclip_similarity(file_path, prompts, clip_model_vit, clip_preprocess_vit, Mclip_model, Mclip_tokenizer)
        sim_clip_vit = np.array(sim_clip_vit.cpu().tolist()[0])
        row_list.append(sim_clip_vit)
    df_clip_vit = pd.DataFrame(row_list, columns=prompts)
    df_clip_vit.to_csv(f'{output_folder}/{output_file}_clipM.csv', index=False)

if __name__ == "__main__":
    main()
