"""Publish only the two verified 0.7 patch assets; keep source archives clean."""
import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request,urlopen

REPO='verylonghong/3ds-kr-patch-girls-mode-4'

def main():
    if os.environ['GITHUB_REPOSITORY']!=REPO:raise RuntimeError('Unexpected repository')
    manifest=json.loads(Path('release-assets-0.7.json').read_text(encoding='utf-8'))
    if manifest['repository']!=REPO or manifest['tag']!='v0.7':raise RuntimeError('Unexpected release manifest')
    root='https://api.github.com/repos/'+REPO
    def api(path,method='GET',body=None,binary=None):
        url=path if path.startswith('https://') else root+path
        if not (url.startswith(root+'/') or url.startswith('https://uploads.github.com/repos/'+REPO+'/')):
            raise RuntimeError('Unexpected GitHub API destination')
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'gs4-korean-release-0.7'}
        data=None
        if body is not None:data=json.dumps(body,ensure_ascii=False).encode();headers['Content-Type']='application/json'
        if binary is not None:data=binary;headers['Content-Type']='application/octet-stream'
        with urlopen(Request(url,data=data,headers=headers,method=method),timeout=120) as response:
            raw=response.read();return json.loads(raw) if raw else None
    target=os.environ['GITHUB_SHA']
    tree=api('/git/trees/'+target+'?recursive=1')
    if tree.get('truncated'):raise RuntimeError('Incomplete source tree')
    paths=[r['path'] for r in tree['tree'] if r['type']=='blob']
    if any(p.startswith('payloads/') or p.endswith(('.xdelta','.zip','.3ds','.cia','.part000')) for p in paths):
        raise RuntimeError('Binary patch payload in release source tree')
    notes=Path('RELEASE_NOTES.md').read_text(encoding='utf-8')
    expected={r['name']:r for r in manifest['assets']}
    if len(expected)!=2:raise RuntimeError('Expected exactly two assets')
    try:release=api('/releases/tags/v0.7')
    except HTTPError as error:
        if error.code!=404:raise
        release=None
    if release and release['target_commitish']!=target:raise RuntimeError('Release target differs; preserve existing release')
    if release and set(a['name'] for a in release['assets'])-expected.keys():raise RuntimeError('Unexpected remote asset')
    payloads={}
    existing={r['name']:r for r in release['assets']} if release else {}
    for name,row in expected.items():
        if name in existing:
            if existing[name]['size']!=row['bytes'] or existing[name].get('digest')!='sha256:'+row['sha256']:
                raise RuntimeError('Existing asset differs: '+name)
            continue
        if release and not release['draft']:raise RuntimeError('Published release has a missing asset')
        payload=bytearray()
        for part in row['parts']:
            blob=api('/git/blobs/'+part['blob_sha'])
            if blob.get('encoding')!='base64' or blob['sha']!=part['blob_sha']:raise RuntimeError('Unexpected blob response')
            data=base64.b64decode(blob['content'])
            if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:raise RuntimeError('Chunk checksum mismatch')
            payload.extend(data)
        if len(payload)!=row['bytes'] or hashlib.sha256(payload).hexdigest()!=row['sha256']:raise RuntimeError('Asset checksum mismatch')
        payloads[name]=bytes(payload)
        print('Verified '+name+' ('+str(len(payload))+' bytes)',flush=True)
    if release is None:
        release=api('/releases','POST',dict(tag_name='v0.7',target_commitish=target,name='걸스 모드 4 한국어 패치 0.7',
            body=notes,draft=True,prerelease=False))
    endpoint='/releases/'+str(release['id'])
    for name,data in payloads.items():
        url=release['upload_url'].split('{',1)[0]+'?name='+quote(name)
        api(url,'POST',binary=data);print('Uploaded '+name,flush=True)
    def verify(remote):
        assets={a['name']:a for a in remote['assets']}
        if len(remote['assets'])!=2 or assets.keys()!=expected.keys():raise RuntimeError('Remote asset count mismatch')
        for name,row in expected.items():
            if assets[name]['size']!=row['bytes'] or assets[name].get('digest')!='sha256:'+row['sha256']:
                raise RuntimeError('Remote asset checksum mismatch: '+name)
    release=api(endpoint);verify(release)
    if release['draft'] or release['body']!=notes:
        release=api(endpoint,'PATCH',dict(draft=False,prerelease=False,body=notes,make_latest='true'))
    verify(release)
    if release['draft']:raise RuntimeError('Release was not published')
    tag=api('/git/ref/tags/v0.7')
    if tag['object']['type']!='commit' or tag['object']['sha']!=target:raise RuntimeError('Tag does not point to clean source commit')
    branch=manifest['payload_branch'];cleanup=False
    if branch!='release-payloads-v0.7':raise RuntimeError('Unexpected temporary branch')
    try:
        ref=api('/git/ref/heads/'+branch)
        if ref['object']['sha']==manifest['payload_commit_sha']:
            api('/git/refs/heads/'+branch,'DELETE');cleanup=True
    except HTTPError as error:
        if error.code!=404:raise
        cleanup=True
    result=dict(release_url=release['html_url'],published=True,source_commit=target,source_archive_patch_payloads=0,
        temporary_payload_branch_removed=cleanup,
        assets=[dict(name=a['name'],bytes=a['size'],digest=a['digest']) for a in release['assets']])
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:
            f.write('Published [v0.7]('+release['html_url']+') with two SHA-256 verified assets and updated screenshots.\n')

if __name__=='__main__':main()
