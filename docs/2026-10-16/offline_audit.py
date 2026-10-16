"""Offline control-flow audit; no model or production request is permitted.

Usage: python offline_audit.py PATH_TO_SNAPSHOT
This deliberately mocks successful model outputs. It cannot verify model quality,
production deployment, media generation, or the full browser experience.
"""
import asyncio, importlib, json, os, socket, sys
from pathlib import Path

target=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(target))
os.environ.pop('GEMINI_API_KEY',None)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def denied(*args,**kwargs): raise AssertionError('Network forbidden in offline audit')
module=importlib.import_module('app')
module.get_genai_client=denied
results=[]
def record(name,passed,detail): results.append({'check':name,'passed':bool(passed),'detail':detail})

async def run():
    # Windows creates a loopback socketpair to initialize its event loop first.
    # Block every connection once that local event loop is initialized.
    socket.socket.connect=denied
    socket.create_connection=denied
    health=await module.health()
    record('health contract',health.get('status')=='ok' and health.get('scope')=='ariadne-epistemic-safety-copilot','Direct Python route invocation; not a container or deployed HTTP check.')
    ready=await module.readiness()
    record('readiness limitation reproduced',not ready['api_key_configured'] and ready['deployment_verified'] is True,'deployment_verified is true without credentials; readiness is not live model proof.')
    tp={'id':'BOOK-1','content':'Library book club meets Saturday. No payment, link, download or personal data requested.','observed_sender_id':'library.example','claimed_persona':'Book club organizer'}
    req=module.AnalyzeRequest(preset_id='custom',touchpoints=[tp],known_contacts=[],simulate_failure='all')
    failure=await module.analyze_json(req)
    # JSON endpoint wraps the result; keep assertions explicit across wrappers.
    failure=failure.get('bundle',failure)
    r2=failure['round2_repaired']
    record('all-stage failure stays failed',failure['telemetry']['overall_status']=='failed' and all(x['status']=='failed' for x in failure['telemetry']['model_call_report'].values()),'Controlled simulate_failure=all with all networking blocked.')
    record('failed synthesis contains no claims or anchors',r2['epistemic_claims_ledger']==[] and r2['out_of_band_anchors']==[],'Empty generated evidence rather than a substituted preset.')
    record('custom input isolation on failure',failure['touchpoints'][0]['id']=='BOOK-1' and failure['known_contacts']==[] and 'TP-01' not in json.dumps(failure),'Original benign custom touchpoint survives; no inherited family preset IDs.')
    try:
        await module.analyze_json(module.AnalyzeRequest(consent_granted=False))
    except module.HTTPException as exc:
        record('explicit consent rejection',exc.status_code==400,'consent_granted=false is rejected; request default remains true and is a separate limitation.')
    module._sync_call_argon_round1=lambda *a:{'summary':'Library book club notice','flawed_assumptions':[]}
    module._sync_call_flash_critic=lambda *a:{'verification_status':'Mocked','defects_found':[]}
    module._sync_call_argon_round2=lambda *a:{'epistemic_risk_band':'VERIFIED_LOW','risk_headline':'Library book club','executive_summary':'The library announced a book club.','epistemic_claims_ledger':[{'claim_id':'BOOK-OBS','statement':'Book club meets Saturday','epistemic_status':'OBSERVED_FACT'}],'tts_briefing_script':'Library book club notice.'}
    module._sync_call_gemma_privacy_packet=lambda *a:{'redacted_summary':'Library notice','questions_for_trusted_contact_or_authority':[]}
    module._sync_call_nano_banana_image=lambda *a:{'generation_mode':'OFFLINE_MOCK'}
    module._sync_call_flash_tts=lambda *a:{'generation_mode':'OFFLINE_MOCK'}
    clean=await module.analyze_json(module.AnalyzeRequest(preset_id='custom',touchpoints=[tp],known_contacts=[]))
    clean=clean.get('bundle',clean)
    encoded=json.dumps(clean)
    record('mocked success isolates custom bundle',clean['known_contacts']==[] and clean['round2_repaired']['epistemic_claims_ledger'][0]['claim_id']=='BOOK-OBS' and 'TP-01' not in encoded,'Control-flow only: every model helper was replaced with a synthetic stub. live_api_success labels here do not establish a real call.')
    record('mode contract mismatch reproduced',module.AnalyzeRequest().mode=='live','Only mode=showcase selects fixture in source; local README described mode=fixture.')

asyncio.run(run())
print(json.dumps({'scope':'offline snapshot control flow only','network':'blocked; no model calls','checks':results,'all_checks_passed':all(x['passed'] for x in results)},indent=2))
if not all(x['passed'] for x in results): raise SystemExit(1)
