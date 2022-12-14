# The Biased Artist: Exploiting Cultural Biases via Homoglyphs in Text-Guided Image Generation Models

  <center>
  <img src="images/concept.jpg" alt="PPA Examples"  height=260>
  </center>

> **Abstract:**
> *Text-guided image generation models, such as DALL-E 2 and Stable Diffusion, have recently received much attention from academia and the general public. Provided with textual descriptions, these models are capable of generating high-quality images depicting various concepts and styles. However, such models are trained on large amounts of public data and implicitly learn relationships from their training data that are not immediately apparent. We demonstrate that common multimodal models implicitly learned cultural biases that can be triggered and injected into the generated images by simply replacing single characters in the textual description with visually similar non-Latin characters. These so-called homoglyph replacements enable malicious users or service providers to induce biases into the generated images and even render the whole generation process useless. We practically illustrate such attacks on DALL-E 2 and Stable Diffusion as text-guided image generation models and further show that CLIP also behaves similarly. Our results further indicate that text encoders trained on multilingual data provide a way to mitigate the effects of homoglyph replacements.*  
[Full Paper (PDF)](https://arxiv.org/pdf/2209.08891.pdf)

## Remarks
The Stable Diffusion model is still under development and might be changed in the future, requiring code changes in the future. We will further improve our code in the next couple of weeks to make it more accessible. 

## Setup Docker Container
The easiest way to perform the attacks is to run the code in a Docker container. To build the Docker image run the following script:

```bash
docker build -t biased_artist  .
```

To create and start a Docker container run the following command from the project's root:

```bash
docker run --rm --shm-size 16G --name my_container --gpus '"device=0"' -v $(pwd):/workspace -it biased_artist bash
```

## Generate Stable Diffusion Images
To reproduce our results from Section *4.3. Homoglyph Susceptibility is Inherent in Text-Guided Generative Models* from the paper and generate the corresponding images, use the scripts ```generate_stable_diffusion_images.py``` and ```generate_stable_diffusion_images_embedding_diff.py```. To load the Stable Diffusion model from Hugging Face, you need to provide the token from a user account. A token can be created at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). Save your token in the ```hf_token``` variables in line 6 or 11, respectively. Further specify the homoglyphs in the ```characters``` tuples in line 7 or 12, respectively. For generating images with homoglyphs in the textual description, specify the prompt and the character to be replaced with homoglyphs in line 36 of ```generate_stable_diffusion_images.py```. For inducing the biases in the embedding space, state the text prompt and the Latin character to compute the difference from in lines 23 and 24 in ```generate_stable_diffusion_images_embedding_diff.py```.

Then run the scripts with one of the following commands:
```bash
python generate_stable_diffusion_images.py
python generate_stable_diffusion_images_embedding_diff.py
```

## Analyze CLIP Models
To reproduce our results from Section *4.4. Non-Generative Multimodal Models Behave Similarly Sensitively* from the paper, use the script ```analyze_clip_models.py```. First, download the input images, for example by using [CommonsDownloader](https://pypi.org/project/CommonsDownloader/) and put them into a folder, which is then specified in the parameter ```img_paths``` in line 13. We provide the URL lists in the folder ```real_samples```. Further, define the ```output_file``` name in line 14 and the different ```prompts``` in line 18. Then run the following command:
```bash
python analyze_clip_models.py
```
The ```create_clip_figures.ipynb``` notebook provides the code to create the CLIP figures from the paper.

## Analyze LAION Datasets
To reproduce our LAION dataset analysis from Section *5.1 Reasons for Model Behavior* from the paper, use the script ```analyze_laion_aesthetics.py```. First, define the ```dataset_path``` from hugging face you want to analyze in line 8. When required, update or extent the lists of characters to search the dataset for in line 11.
Then run the following command:
```bash
python analyze_laion_aesthetics.py
```
Please note that the download and analysis of the dataset takes its time and might run a few days. If the process is stopped, just re-run the script to continue. Already searched files will be skipped. The final results will be written to ```dataset_analysis.csv```. Intermediate results for each parquet file will be stored at ```/laion_aestetics_results_per_file```.

## Citation
If you build upon our work, please don't forget to cite us.
```
@article{struppek22biasedartist,
  author = {Struppek, Lukas and Hintersdorf, Dominik and Kersting, Kristian},
  title = {The Biased Artist: Exploiting Cultural Biases via Homoglyphs in Text-Guided Image Generation Models},
  journal = {arXiv preprint},
  volume = {arXiv:2209.08891},
  year = {2022},
}
```


## Packages and Repositories
Some of our analyses rely on other repos and pre-trained models. We want to thank the authors for making their code and models publicly available. For license details, refer to the corresponding files in our repo. For more details on the specific functionality, please visit the corresponding repos.

- CLIP: https://github.com/openai/CLIP
- Open-CLIP: https://github.com/mlfoundations/open_clip
- Multilingual CLIP: https://github.com/FreddeFrallan/Multilingual-CLIP
- Stable Diffusion: https://github.com/CompVis/stable-diffusion
