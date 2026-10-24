# Character pipeline: original Git history index

This branch records the local history of the character-generation pipeline and is not a copy of its original Git object database.

**Original local Git repository:** hypermasculine-character-system  
**Intended canonical branch:** `charflow/independent-images`  
**Original root commit:** `682dd1c4ec820c4e77cf217cac7e44107c24c8ec`  
**Original HEAD:** `a10739f23218ccc297e2ed476829bba5306f94cf`  
**Original commits:** 98, linear  
**Original source PNGs approved:** 3  
**Rejected PNGs tracked locally:** 16  
**Local bundle:** `canonical-local-history.bundle` (complete 98-commit history, 40 MiB approximate). SHA-256: `43f5e6a9359798b5b9e4b324e35a1f22d69a02285f0378c975bde5fae179c426`.

The file [history/LOCAL_COMMITS.txt](history/LOCAL_COMMITS.txt) lists all 98 original abbreviated SHAs and messages in chronological order. The original full commit IDs, authors, dates, trees, and binary blobs remain inside the **local** Git repository and full-history bundle.

## Important limitations

The connected GitHub app can create blobs, trees, and commits, but its current commit API does **not** let us submit the exact author, committer, timezone, and timestamp metadata of arbitrary existing commits. GitHub would compute different IDs if we replayed the commits using the API.

The local container cannot make a working outbound Git connection, and the connector cannot dereference local `/mnt/data` files. The binary PNG objects have therefore **not** been transferred. The history-index branch is not a canonical historical push.

Do not substitute this index branch for the canonical `charflow/independent-images` branch.

## Canonical push when Git transport is available

From the original local Git repository, run:

```bash
git bundle verify /path/to/canonical-local-history.bundle
git push https://github.com/cawolfdev/test.git \
  a10739f23218ccc297e2ed476829bba5306f94cf:refs/heads/charflow/independent-images
git ls-remote https://github.com/cawolfdev/test.git refs/heads/charflow/independent-images
```

This command is a normal non-force push; it uploads the complete canonical commit graph and binary objects under their unchanged object IDs. Only claim completion after the remote branch reports HEAD `a10739f23218ccc297e2ed476829bba5306f94cf`.

The original working tree also has an uncommitted change to `prompts/image_1_4.txt`; that change is excluded from the 98-commit history and should be reviewed separately.
