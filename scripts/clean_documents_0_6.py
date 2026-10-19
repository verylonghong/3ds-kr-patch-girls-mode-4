"""Remove detailed change documents/links from the published v0.6 sources."""
import json
import os
import re
from urllib.request import Request,urlopen

REPO='verylonghong/3ds-kr-patch-girls-mode-4'
OLD_TAG='95674eda07adfc87d7e94507cf5b00f73cfaf0ce'
EXPECTED={
    'GS4_Korean_Repack_v0.6.zip':(654950370,57266196,'sha256:9a46f249aea30058b65de0b563af10936da7baefba79363ca4c825a4b58c60e8'),
    'GS4_Korean_v0.6_From_Japan_3DS.xdelta':(654950332,7394563,'sha256:3a30e4aa34195b89d64f8f0be822f227abf1dec0f122a526c4d3595880b0e3c9'),
}

def main():
    if os.environ['GITHUB_REPOSITORY']!=REPO:raise RuntimeError('Unexpected repository')
    root='https://api.github.com/repos/'+REPO;target=os.environ['GITHUB_SHA']
    def api(path,method='GET',body=None):
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'gs4-v0.6-document-cleanup'}
        data=None
        if body is not None:data=json.dumps(body,ensure_ascii=False).encode();headers['Content-Type']='application/json'
        with urlopen(Request(root+path,data=data,headers=headers,method=method),timeout=60) as response:return json.load(response)
    def verify_release(release):
        if release['id']!=416825547 or release['draft'] or release.get('immutable'):raise RuntimeError('Unexpected/immutable release')
        assets={a['name']:(a['id'],a['size'],a.get('digest')) for a in release['assets']}
        if assets!=EXPECTED:raise RuntimeError('Release attachments differ')
    tree=api('/git/trees/'+target+'?recursive=1')
    if tree.get('truncated'):raise RuntimeError('Incomplete source tree')
    paths=[r['path'] for r in tree['tree'] if r['type']=='blob']
    if any(p=='CHANGELOG.md' or p.startswith('changes/') for p in paths):raise RuntimeError('Requested documents still exist')
    if any(p.startswith('payloads/') or p.endswith(('.xdelta','.zip','.3ds','.cia')) for p in paths):raise RuntimeError('Patch/game binary in source tree')
    release=api('/releases/tags/v0.6');verify_release(release)
    tag=api('/git/ref/tags/v0.6')
    if tag['object']['type']!='commit' or tag['object']['sha'] not in (OLD_TAG,target):raise RuntimeError('Tag changed unexpectedly')
    body=release.get('body') or ''
    clean=re.sub(r'^\[0\.5 이후 전체 변경 내역\]\([^\r\n]*CHANGELOG\.md\)[^\r\n]*(?:\r?\n){0,2}','',body,flags=re.M)
    if re.search(r'CHANGELOG\.md|/changes/',clean,re.I):raise RuntimeError('Unhandled link to removed documents')
    if clean!=body:api('/releases/'+str(release['id']),'PATCH',dict(body=clean))
    if tag['object']['sha']!=target:api('/git/refs/tags/v0.6','PATCH',dict(sha=target,force=True))
    after=api('/releases/tags/v0.6');verify_release(after)
    if after.get('body')!=clean:raise RuntimeError('Release notes not updated')
    if api('/git/ref/tags/v0.6')['object']['sha']!=target:raise RuntimeError('Source tag not updated')
    result=dict(release_url=after['html_url'],source_commit=target,deleted=['CHANGELOG.md','changes/'],
        release_links_removed=True,release_attachments_unchanged=True,source_archives_updated=True)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:f.write('Removed CHANGELOG.md and changes/ from v0.6 source archives and cleaned links. Patch attachments unchanged.\n')

if __name__=='__main__':main()

