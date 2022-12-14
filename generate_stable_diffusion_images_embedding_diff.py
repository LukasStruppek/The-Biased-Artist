from torch import autocast
from diffusers import AutoencoderKL, UNet2DConditionModel, LMSDiscreteScheduler
import torch
from PIL import Image
from transformers import CLIPTextModel, CLIPTokenizer
from tqdm.auto import tqdm
from torch import autocast
from tqdm.auto import tqdm
import os

hf_token = 'INSERT_HF_TOKEN'
characters = (
    ('latin', 'o'),
    ('oriya', '୦'),
    ('osmanya𐒆', '𐒆'),
    ('latin_ext', 'ọ'),
    ('nko', 'ߋ'),
    ('hangul', 'ㅇ'),
    ('arabic', 'ه'),
    ('armenian', 'օ'),
    ('bengali', '০')
)
prompt = [f'A man sitting at a table']
latin_character = 'o'

def main():
    vae = AutoencoderKL.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="vae", use_auth_token=hf_token)
    tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
    text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14")
    unet = UNet2DConditionModel.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="unet", use_auth_token=hf_token)

    scheduler = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", num_train_timesteps=1000)

    torch_device = "cuda"
    vae.to(torch_device)
    text_encoder.to(torch_device)
    unet.to(torch_device) 

    os.makedirs('stable_diffusion_images', exist_ok=True)

    def generate_image(prompt, bias_prompt):
        height = 512                        # default height of Stable Diffusion
        width = 512                         # default width of Stable Diffusion
        num_inference_steps = 100           # Number of denoising steps
        guidance_scale = 7.5                # Scale for classifier-free guidance
        # generator = torch.manual_seed(seed)    # Seed generator to create the inital latent noise
        batch_size = len(prompt)

        text_input_bias = tokenizer(bias_prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt")
        text_embeddings_bias = text_encoder(text_input_bias.input_ids.to(torch_device))[0]
        bias = (text_embeddings_bias[1] - text_embeddings_bias[0]).unsqueeze(0)

        text_input = tokenizer(prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt")
        text_embeddings = text_encoder(text_input.input_ids.to(torch_device))[0]
        text_embeddings = (text_embeddings + bias)

        max_length = text_input.input_ids.shape[-1]
        uncond_input = tokenizer(
            [""] * batch_size, padding="max_length", max_length=max_length, return_tensors="pt"
        )
        uncond_embeddings = text_encoder(uncond_input.input_ids.to(torch_device))[0]   
        text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

        latents = torch.randn(
            (batch_size, unet.in_channels, height // 8, width // 8),
            generator=generator,
        )
        latents = latents.to(torch_device)
        scheduler.set_timesteps(num_inference_steps)
        latents = latents * scheduler.sigmas[0]

        with autocast("cuda"):
            for i, t in tqdm(enumerate(scheduler.timesteps)):
                # expand the latents if we are doing classifier-free guidance to avoid doing two forward passes.
                latent_model_input = torch.cat([latents] * 2)
                sigma = scheduler.sigmas[i]
                latent_model_input = latent_model_input / ((sigma**2 + 1) ** 0.5)

                # predict the noise residual
                with torch.no_grad():
                    noise_pred = unet(latent_model_input, t, encoder_hidden_states=text_embeddings)["sample"]

                # perform guidance
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

                # compute the previous noisy sample x_t -> x_t-1
                latents = scheduler.step(noise_pred, i, latents).prev_sample
                torch.cuda.empty_cache()

            latents = 1 / 0.18215 * latents
            image = vae.decode(latents).sample
            image = (image / 2 + 0.5).clamp(0, 1)
            image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
            images = (image * 255).round().astype("uint8")
            pil_images = [Image.fromarray(image) for image in images]
        return pil_images[0]

    for script, c in characters:
        chars = [latin_character, c]
        file_name = f'embedding_bias_{script}'
        generator = torch.manual_seed(1)

        for i in range(4):
            with autocast("cuda"):
                image = generate_image(prompt, chars)
        
            image.save(f"stable_diffusion_images/{file_name}_{i}.jpg")


if __name__ == "__main__":
    main()
