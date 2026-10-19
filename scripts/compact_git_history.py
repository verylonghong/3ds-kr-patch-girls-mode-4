"""Remove historical patch blobs while retaining every current ref tree and release asset."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.request import Request,urlopen

REPO='verylonghong/3ds-kr-patch-girls-mode-4'
ROOT=Path.cwd().resolve()
MIRROR=ROOT/'git-history-work/repository.git'
BACKUP=ROOT/'git-history-backup'
REPORT=ROOT/'git-history-report'
STATE=BACKUP/'before.json'
EXPECTED_TAGS={
    'refs/tags/v0.5':'7257dc0912917cdf3d636246979d5dc5586b9e79',
    'refs/tags/v0.6':'cb3361efe9d6036140b80f7d28b3f7722ce2d0d0',
}
PATCH_PATHS=[
    'patches/0.5/GS4_Korean_Repack_v0.5.zip',
    'patches/0.5/GS4_Korean_v0.5_From_Japan_3DS.xdelta',
]

def require(condition,message):
    if not condition:raise RuntimeError(message)

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def api(path):
    headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28','User-Agent':'gs4-history-maintenance'}
    with urlopen(Request('https://api.github.com/repos/'+REPO+path,headers=headers),timeout=60) as response:return json.load(response)

def git(*args,cwd=MIRROR):
    env=os.environ.copy()
    # Keep the credential out of URLs, command arguments and recorded output.
    auth=base64.b64encode(('x-access-token:'+env['GH_TOKEN']).encode()).decode()
    env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
        GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+auth,GIT_TERMINAL_PROMPT='0')
    result=subprocess.run(['git',*map(str,args)],cwd=cwd,env=env,capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError('git '+str(args[0])+' failed: '+result.stderr[-4000:])
    return result.stdout.strip()

def refs():
    return dict(line.split(' ',1) for line in git('for-each-ref','--format=%(refname) %(objectname)').splitlines())

def server_refs():
    heads=api('/git/matching-refs/heads/');tags=api('/git/matching-refs/tags/')
    require(all(r['object']['type']=='commit' for r in heads+tags),'Unexpected annotated/non-commit ref')
    return {r['ref']:r['object']['sha'] for r in heads+tags}

def release_snapshot():
    result={}
    for tag in ('v0.5','v0.6'):
        r=api('/releases/tags/'+tag)
        require(not r['draft'] and not r.get('immutable'),'Unexpected release state')
        result[tag]=dict(id=r['id'],tag=r['tag_name'],body=r.get('body'),draft=r['draft'],prerelease=r['prerelease'],
            assets=sorted([dict(id=a['id'],name=a['name'],bytes=a['size'],digest=a.get('digest')) for a in r['assets']],key=lambda a:a['name']))
        require(len(result[tag]['assets'])==2,'Unexpected release asset count')
    return result

def tip_trees(mapping):return {ref:git('rev-parse',ref+'^{tree}') for ref in mapping}

def object_bytes():return sum(p.stat().st_size for p in (MIRROR/'objects').rglob('*') if p.is_file())

def history_patch_paths():
    found=set()
    for commit in git('rev-list','--all').splitlines():
        for name in git('ls-tree','-r','--name-only',commit).splitlines():
            if name.endswith('.xdelta') or (name.endswith('.zip') and 'GS4_Korean_Repack_' in name) or name.startswith('payloads/'):
                found.add(name)
    return sorted(found)

def prepare():
    require(not MIRROR.exists() and not STATE.exists(),'Preserve previous mirror/backup')
    require(MIRROR.resolve().is_relative_to(ROOT),'Mirror outside workspace')
    live=server_refs();expected={'refs/heads/main':os.environ['GITHUB_SHA'],**EXPECTED_TAGS}
    require(live==expected,'Remote refs changed before backup')
    MIRROR.parent.mkdir(parents=True);BACKUP.mkdir();REPORT.mkdir()
    git('clone','--mirror','https://github.com/'+REPO+'.git',MIRROR,cwd=ROOT)
    require(refs()==live,'Mirror refs differ from server')
    paths=history_patch_paths();require(paths==sorted(PATCH_PATHS),'Unexpected historical patch paths')
    commits=git('rev-list','--count','--all')
    bundle=BACKUP/'before-cleanup.bundle'
    git('bundle','create',bundle,'--all');git('bundle','verify',bundle)
    state=dict(repository=REPO,refs=live,tip_trees=tip_trees(live),releases=release_snapshot(),
        removed_paths=paths,object_bytes_before=object_bytes(),reachable_commits_before=int(commits),
        bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bundle_bytes=bundle.stat().st_size,
        backup_verified=True,source_workflow_commit=os.environ['GITHUB_SHA'])
    save(STATE,state);save(REPORT/'before.json',state)
    print(json.dumps(dict(backup_verified=True,bundle_bytes=state['bundle_bytes'],bundle_sha256=state['bundle_sha256'],removed_paths=paths),indent=2),flush=True)

def rewrite():
    state=json.loads(STATE.read_bytes())
    require(state['repository']==REPO and state['backup_verified'],'Invalid backup state')
    bundle=BACKUP/'before-cleanup.bundle'
    require(hashlib.sha256(bundle.read_bytes()).hexdigest()==state['bundle_sha256'],'Backup changed')
    git('bundle','verify',bundle)
    require(refs()==state['refs'] and server_refs()==state['refs'],'Refs changed after backup')
    require(release_snapshot()==state['releases'],'Release changed after backup')
    command=['filter-repo','--force','--invert-paths','--replace-refs','delete-no-add']
    for path in state['removed_paths']:command.extend(['--path',path])
    git(*command)
    after=refs();require(after.keys()==state['refs'].keys(),'Ref names changed')
    require(tip_trees(after)==state['tip_trees'],'Current branch/tag file trees changed')
    require(not history_patch_paths(),'Historical patch paths remain')
    objects=git('rev-list','--objects','--all').splitlines()
    require(not any(any(line.endswith(' '+p) for p in state['removed_paths']) for line in objects),'Patch objects still reachable')
    commit_map=MIRROR/'filter-repo/commit-map'
    require(commit_map.is_file(),'Missing commit map')
    (REPORT/'commit-map.txt').write_bytes(commit_map.read_bytes())
    git('reflog','expire','--expire=now','--all');git('gc','--prune=now')
    result=dict(repository=REPO,removed_paths=state['removed_paths'],before_refs=state['refs'],after_refs=after,
        current_branch_and_tag_trees_preserved=True,release_attachments_preserved=True,
        object_bytes_before=state['object_bytes_before'],object_bytes_after=object_bytes(),
        reachable_commits_before=state['reachable_commits_before'],reachable_commits_after=int(git('rev-list','--count','--all')),
        backup_sha256=state['bundle_sha256'],backup_verified=True,remote_updated=False)
    save(REPORT/'verification.json',result)
    # Check all old heads/tags immediately before one atomic, leased update.
    require(server_refs()==state['refs'],'Remote refs changed before push')
    require(release_snapshot()==state['releases'],'Release changed before push')
    if 'origin' not in git('remote').splitlines():git('remote','add','origin','https://github.com/'+REPO+'.git')
    options=['push','--atomic']+['--force-with-lease='+ref+':'+sha for ref,sha in state['refs'].items()]
    git(*options,'origin',*[ref+':'+ref for ref in after])
    require(server_refs()==after,'Published refs differ from filtered refs')
    require(release_snapshot()==state['releases'],'Release metadata/attachments changed')
    result.update(remote_updated=True,releases_verified_unchanged=True,
        object_bytes_reduced=result['object_bytes_before']-result['object_bytes_after'],
        server_storage_reclamation='GitHub-managed; API size may update later')
    save(REPORT/'verification.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:
            f.write('Historical patch files removed from all branch/tag histories. Current file trees and both releases verified unchanged.\n\n')
            f.write('Mirror object bytes: '+str(result['object_bytes_before'])+' → '+str(result['object_bytes_after'])+'.\n')

if __name__=='__main__':
    require(os.environ.get('GITHUB_REPOSITORY')==REPO,'Unexpected repository')
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true');group.add_argument('--rewrite',action='store_true')
    args=parser.parse_args();prepare() if args.prepare else rewrite()
