// Read only: probe an explicitly selected installed DSH provider in isolated roots.
// No server, account, model, config, watcher, subprocess or personal root is loaded.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
const [providerFile, scratch, mode='installed'] = process.argv.slice(2);
if (!providerFile || !scratch) throw new Error('Usage: node check_dsh_provider.mjs <provider lib/index.js> <fixture root> [installed|uninstalled]');
const {FileSystemSkillProvider} = await import(pathToFileURL(resolve(providerFile)).href);
const signal = new AbortController().signal;
const warnings = [];
const project=join(scratch,'project'), cwd=join(project,'chapters','nested');
const provider = new FileSystemSkillProvider({get:()=>undefined,logger:{warn:(...args)=>warnings.push(args)}},
  {signal,invalidate:()=>{}}, {dshHome:join(scratch,'custom dsh data'),agentsHome:join(scratch,'empty-agents'),watch:false});
const checks=[];
function record(name,ok) { assert.ok(ok,name); checks.push({name,passed:true}); }
try {
  const value=await provider.list({cwd,signal});
  const candidates=Array.isArray(value)?value:value.candidates;
  const user=candidates.find(c=>c.name==='letsgal-authoring' && c.source==='user-dsh');
  const proj=candidates.find(c=>c.name==='letsgal-authoring' && c.source==='project-dsh');
  record('official provider discovers project at nearest Git root', !!proj && proj.locator.path===join(project,'.dsh','skills','letsgal-authoring','SKILL.md'));
  if (mode==='installed') {
    record('official provider discovers personal skill',!!user);
    const loaded=await provider.get(user,{cwd,signal});
    const expectedVersion=JSON.parse(await readFile(new URL('../bundle.json',import.meta.url),'utf8')).version;
    record('official provider loads workflow and metadata',loaded.content.includes('Git') && loaded.metadata.version===expectedVersion);
    record('relative reference is accessible',(await readFile(join(loaded.resourceBase.path,'references','json.md'),'utf8')).includes('JSON'));
  } else { record('uninstalled personal copy is not discovered',!user); }
  record('no parsing warnings',warnings.length===0);
} finally { await provider.dispose(); }
console.log(JSON.stringify({checks,mode}));
