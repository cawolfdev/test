# Hypermasculine character image pipeline

**Purpose:** Independently generate 24 individual character images, in depth-first order, then assemble three 8-character attribute studies. Each output must be a distinct *text-to-image* operation. Prior outputs are never used as image inputs, rescaled into other character images, or cropped into synthetic "generations."

## Actual production state

Check `python charflow.py status` and `git log --oneline`. Empty image directories mean **not generated**. Do not confuse the prompt plan with completed images or the GitHub remote with the local Git repository.

## Design constraints

- 24 individual source images, `images/image_1_1.png` through `images/image_3_8.png`.
- 24 separate context-free prompts saved in `prompts/`, **one full prompt per independent request**.
- Attribute 1 is M (muscle), 2 is A (masculine presence), 3 is F (skeletal/face features); levels 1× through 8× inside each attribute.
- Nonvarying dimensions locked to 1× at every step. **1× muscle means 400% of elite professional bodybuilder muscular bulk**; 1× does not mean human normal.
- Single figure per image. No composite sheets or multi-character image generations.
- A prompt is shown and committed before submission; output image + hash are committed separately; human review commits approval before the next step.
- **Depth-first**: finish and approve `image_1_1` before `image_1_2`. Finish attribute M before A, then F. No character-level parallelism.
- Individual prompt files and generated source images are never created by cropping a previous output. Composites are rendered last using approved source images, with letterboxing and scaling of tiles only; original source files remain byte-for-byte unchanged.

## Manual steps

Requires Python 3.10+, Git, and optionally a direct OpenAI API key for unattended generation.

```bash
python charflow.py status            # Current image and audit status
python charflow.py next              # Display exactly one full prompt and expected output
python charflow.py prepare-next      # Commit that prompt and request settings BEFORE any generation
python charflow.py generate-next     # Submit exactly one n=1 fresh API generation; print prompt; commit PNG+hash
# OR: generate one independent PNG yourself, save it, then import:
python charflow.py import-next /absolute/path/to/single_image.png --source "Manual independent T2I generation"
python charflow.py approve-next --notes "Reviewed full body, isolated attribute, anatomy, framing"
python charflow.py status
```

`generate-next` prompts for typed authorization per API call. Use `OPENAI_API_KEY` in your environment, **never in the repository**. The API is billed separately from ChatGPT. No API key is bundled. Settings in `charflow.py` currently use the direct Images API with the configurable `CHARFLOW_IMAGE_MODEL` (default `gpt-image-1`), `n=1`, `size=1024x1536`, `quality=high`, `output_format=png`, subject to current model availability and API billing. If availability or API schema changes, adjust the explicitly recorded request settings before submitting.

To reject a generated image without advancing, run `python charflow.py reject-next --notes "reason"`, then `prepare-next` again for a distinct attempt. Rejected images and their request records are retained under `rejected/` with a new commit; they are not silently overwritten.

After all eight images for an attribute are approved:

```bash
python -m pip install Pillow
python charflow.py compose --attribute 1
# For attributes 2 and 3, repeat after completion.
```

`compose` produces `composites/image_1.png`, etc., from *approved* full source images. It never calls an image generation model or modifies `images/image_#_#.png`. Composites are disabled until all eight individual source files for their attribute have been approved.

## Publish to existing GitHub repository

**Remote:** `https://github.com/cawolfdev/test.git`  
**Isolated remote branch:** `charflow/independent-images`  
**Do not overwrite** `main`, another branch or unrelated repository files. 

The `origin` remote is configured in the local Git clone. This is only a URL setting,
**not proof of GitHub authentication or that anything has been uploaded**. Verify
GitHub permissions, then run:

```bash
git remote -v
git ls-remote origin HEAD      # verify readable (may be private)
git push -u origin HEAD:refs/heads/charflow/independent-images
```

If the remote branch already exists, non-fast-forward pushes will fail instead of
silently overwriting anything. Do not use `--force`. The local workflow keeps its
complete history in the downloadable Git bundle until GitHub access is restored.

Once the first push succeeds, set `CHARFLOW_PUSH=1` **before running each generation
step** if replication is mandatory. With this flag, every state-changing `charflow.py`
commit pushes to the above branch. A failed push aborts the command and requires
resynchronization before continuing. Do not set `CHARFLOW_PUSH` to a personal token;
use your normal Git authentication instead.

To audit a generated chart that violates the one-character contract (without ever
putting it in `images/`):

```bash
python charflow.py void-next /path/to/bad_chart.png --notes "Eight figures; reject"
python charflow.py prepare-next
```


## Auditing

```bash
git log --oneline --reverse
python charflow.py audit
python charflow.py next
```

Every submission is recorded in `submissions/` before the request; every generation in `images/` plus `results/` including prompt hash, PNG checksum, response request ID if provided, and model name. A failed HTTP call is recorded in `failures/`. Imports explicitly record their manual provenance and cannot independently prove origin. All output-producing steps commit before the next step. GitHub push is optional and its failure does not erase local commits. Never claim remote replication without confirmed `git push` success.
