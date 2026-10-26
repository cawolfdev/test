"""Migrate historical attempts; project evidence logic lives in src/orbit/evidence.py."""
from pathlib import Path
from src.orbit.evidence import record_rejected_attempts,render_all_visibility_diagnostics,inspect_evidence


def main():
    repo=Path(__file__).resolve().parent
    known=[p for p in repo.parent.glob('*.png')
           if not p.name.startswith(('wildlife-bodybuilder-','masktest_','overlaytest_'))]
    result=record_rejected_attempts(repo,known)
    print('Stored',result['count'],'historical unaccepted attempts',flush=True)
    render_all_visibility_diagnostics(repo)
    print(inspect_evidence(repo),flush=True)

if __name__=='__main__':main()
