from torch import autocast
from diffusers import StableDiffusionPipeline, LMSDiscreteScheduler
import torch
import os


hf_token = 'INSERT_HF_TOKEN'
characters = (
        ('latin', 'o'),
        ('oriya', '୦'),
        ('osmanya', '𐒆'),
        ('latin_extended', 'ọ'),
        ('nko', 'ߋ'),
        ('hangul', 'ㅇ'),
        ('arabic', 'ه'),
        ('armenian', 'օ'),
        ('bengali', '০')
    )


def main():
    lms = LMSDiscreteScheduler(
        beta_start=0.00085, 
        beta_end=0.012, 
        beta_schedule="scaled_linear"
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4", 
        scheduler=lms,
        use_auth_token=hf_token
    ).to("cuda")

    os.makedirs('stable_diffusion_images', exist_ok=True)

    for script, c in characters:
        prompt = f'A photo {c}f an actress'
        file_name = f'actress_{script}'
        torch.manual_seed(1)

        for i in range(4):
            with autocast("cuda"):
                image = pipe(prompt, num_inference_steps=100)["sample"][0]  
                
            image.save(f"stable_diffusion_images/{file_name}_{i}.jpg")

if __name__ == "__main__":
    main()
