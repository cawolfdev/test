from src.orbit.core import *  # existing import path smoke test
from tools.git_bridge import batches, git_blob_sha

def test_git_blob_hash_matches_known_git_example():
    assert git_blob_sha(b'hello\n') == 'ce013625030ba8dba906f756967f9e9ca394464a'

def test_batch_preserves_order_and_completeness():
    entries = [{'data':'A'*120,'path':str(i)} for i in range(7)]
    result = list(batches(entries,250))
    assert [row['path'] for batch in result for row in batch] == [str(i) for i in range(7)]
    assert all(batch for batch in result)
