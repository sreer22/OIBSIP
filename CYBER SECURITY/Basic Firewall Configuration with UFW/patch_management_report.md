# The Importance of Patch Management

**Research report | 6 October 2026**

## Executive summary

Patch management is the repeatable work of finding, prioritizing, acquiring, testing, deploying, and verifying software updates across an organization. It is preventive maintenance as well as a security control: a disclosed vulnerability can become a practical entry point once attackers know how to exploit it. Patches cannot eliminate every risk, but a disciplined, measurable process reduces the time that vulnerable systems remain exposed.

Two major incidents show the consequences of missing that window. WannaCry spread using the Windows SMB vulnerability addressed by Microsoft’s MS17-010 update before the outbreak. The Equifax breach involved a known Apache Struts flaw for which a patch had been released before attackers compromised the company. Good patching is more than “install every update immediately”: organizations need an accurate inventory, risk-based priorities, safe testing, controlled rollout, verification, and a documented exception path for systems that cannot be updated promptly.

## 1. What patch management is

NIST defines enterprise patch management as identifying, prioritizing, acquiring, installing, and verifying patches, updates, and upgrades throughout an organization. NIST frames it as preventive maintenance—not an occasional emergency task—and recommends that organizations create an enterprise strategy that reduces risk while supporting their mission [1].

Patch management sits within the vulnerability lifecycle:

1. A flaw is discovered by a vendor, researcher, customer, or attacker.
2. The flaw is reported and analyzed; a vendor may develop a fix or mitigation.
3. The weakness may receive a **CVE identifier**, a standardized reference for the vulnerability. A CVE identifier helps teams and tools refer to the same issue; it is not itself a severity rating or proof that a particular organization is vulnerable [2].
4. Advisories, vulnerability databases, and security teams publish details. The NIST National Vulnerability Database (NVD) enriches CVE records with information such as affected products and Common Vulnerability Scoring System (CVSS) assessments when available [3].
5. Attackers may develop or reuse exploit code. CISA’s **Known Exploited Vulnerabilities (KEV) Catalog** identifies vulnerabilities with evidence of exploitation in the wild; this evidence is a strong prioritization signal [4].
6. The organization identifies affected assets, applies a patch or an effective mitigation, and verifies the exposure has been removed.

CVSS communicates vulnerability **severity**, using technical characteristics and scores from 0 to 10; it is not a complete measure of business risk. FIRST explicitly cautions that CVSS should not be used alone to assess risk. A high score matters, but so do active exploitation, internet exposure, asset criticality, available mitigations, and the potential impact to the organization [5].

## 2. Why patches matter

A vulnerability is a weakness; an exploit is a way to take advantage of it. Public advisories and proof-of-concept code can help defenders understand and fix a flaw, but they can also lower the effort required for attackers to target it. A patch closes a known weakness in affected software. Until the update is installed—or an effective compensating control is applied—the vulnerable code may remain reachable.

The exposure window matters. An organization cannot control when a vendor discovers or discloses a flaw, but it can reduce the time between notification and verified remediation. Attackers also scan broadly: a system may be targeted because it is exposed and vulnerable, not because the organization is individually selected.

### Case study: WannaCry and EternalBlue (2017)

Microsoft released the MS17-010 security update for the Windows SMB vulnerability on **14 March 2017**. The WannaCry outbreak began on **12 May 2017** and used the EternalBlue SMBv1 exploit to propagate ransomware between vulnerable systems. CISA reported widespread impact across **more than 150 countries** and tens of thousands of infections; Microsoft said systems that had installed MS17-010 were protected against the specific vulnerability used by WannaCry [6][7].

The lesson is not that every affected organization had the same patch process or that patching alone prevents all ransomware. Rather, a known network-facing vulnerability plus delayed or incomplete remediation can turn one compromised system into a path to many others. Unsupported systems that cannot receive normal updates require an explicit isolation, replacement, or compensating-control plan.

### Case study: Equifax and Apache Struts (2017)

Attackers exploited the Apache Struts vulnerability **CVE-2017-5638** in Equifax’s online dispute portal. The U.S. House Committee on Oversight and Government Reform’s investigative report and the Government Accountability Office’s review describe the breach and shortcomings in Equifax’s vulnerability and patch management [8][9]. The vulnerability had been disclosed and a fix made available before the attackers accessed the system. This was not a Windows EternalBlue incident: it involved a different product and a different missed remediation opportunity.

The incident exposed personal information relating to approximately **147 million people**. In 2019, the Federal Trade Commission announced a settlement of at least **$575 million**, with a fund that could increase the total to as much as **$700 million**, to resolve federal and state claims related to the breach [10]. Those figures illustrate legal and remediation consequences, not a universal price tag for an unpatched vulnerability.

Together, the cases demonstrate why organizations need asset ownership, reliable advisory intake, prioritization, deadlines, escalation, verification, and reporting. “An update was released” is not the same as “every affected asset was identified and fixed.”

## 3. Consequences of not patching

Unpatched systems can leave known weaknesses exploitable long after fixes are available. Potential consequences include:

- **Unauthorized access and data exposure:** attackers may read, alter, or exfiltrate personal, financial, health, or intellectual-property data.
- **Ransomware and operational disruption:** remote-code-execution flaws and vulnerable services can support malware deployment, lateral movement, encryption, or service outages.
- **Recovery and response expense:** incident investigation, legal support, notification, identity protection, restoration, and customer remediation can exceed the cost of routine maintenance.
- **Regulatory, contractual, and legal consequences:** organizations may face investigations, claims, fines, or corrective-action requirements if controls were inadequate or reporting obligations are missed. The Equifax settlement is one documented example [10].
- **Loss of trust and business:** downtime and public disclosures can affect customers, partners, revenue, and future contracts.
- **Safety and mission impact:** in health care, industrial environments, and critical services, an outage can affect delivery of essential services and, in some settings, physical safety.

**Cost statistic, with scope:** IBM’s *Cost of a Data Breach Report 2025* reports a **$4.44 million global average cost per data breach** [11]. This is an average across studied breaches, not an estimate of the cost of patch failure specifically and not a prediction for any one organization. Actual impact varies with industry, jurisdiction, records involved, detection time, and response capability.

The WannaCry and Equifax figures above provide more directly relevant evidence of the scale of real incidents: a ransomware campaign affecting organizations in over 150 countries and a breach affecting roughly 147 million people followed by a settlement that could reach $700 million [6][10].

## 4. Patch management lifecycle

| Phase | What the organization does | Evidence of completion |
|---|---|---|
| **1. Discovery** | Maintain an inventory of hardware, operating systems, applications, libraries, cloud images, firmware, and dependencies. Identify owners, versions, exposure, business purpose, and end-of-support status. Subscribe to vendor advisories, CISA KEV, and relevant vulnerability feeds. | Inventory coverage and an affected-asset list with accountable owners. |
| **2. Assessment** | Match advisories to deployed versions. Assess severity, confirmed exploitation, internet reachability, asset criticality, business impact, and available workarounds. Use CVSS as an input—not the sole priority score—and raise priority when a vulnerability is in KEV or actively targeted. | A risk-ranked remediation queue, target dates, and documented decisions. |
| **3. Testing** | Validate the patch in a representative test or staging environment. Check application behavior, integrations, security controls, performance, and rollback or recovery steps. For urgent exploitation, use an expedited, risk-appropriate test rather than allowing testing to become an indefinite delay. | Test results, known issues, implementation and rollback plans, and an approved change. |
| **4. Deployment** | Roll out by controlled rings or maintenance windows: pilot, limited production, then broader fleet. Prioritize exposed and high-impact systems. Coordinate with service owners, use configuration management where possible, and protect update packages and deployment credentials. | Deployment records and status by asset, version, and change window. |
| **5. Verification** | Confirm the installed version or patch state with endpoint, vulnerability, configuration, or application checks. Rescan affected assets, test service health, look for failed or offline endpoints, and confirm a mitigation is effective where patching is not yet possible. | Verified compliant asset state, exceptions with owners and expiry dates, and tracked failures. |

These phases form a continuous loop: new assets and advisories keep entering the process, and verification findings feed back into inventory and deployment planning. A dashboard showing “patch job succeeded” is not enough if devices were offline, excluded, or reporting stale data.

## 5. Prioritized seven-step patch management checklist

1. **Know what you own.** Build and maintain a complete, machine-readable asset and software inventory; include cloud workloads, internet-facing services, endpoints, network appliances, and third-party components. Assign owners and identify end-of-life systems.
2. **Continuously find relevant updates.** Monitor vendor advisories, operating-system and application update channels, CISA KEV, and vulnerability scanners. Map CVEs and vendor notices to installed products and versions.
3. **Prioritize by risk and exploitation.** Put actively exploited vulnerabilities, KEV-listed items, exposed services, critical business assets, and vulnerabilities with severe impact at the top. Use CVSS severity as one factor alongside exposure and business context. Define emergency and routine remediation targets that fit the organization’s risk tolerance.
4. **Set an accountable deadline.** Record an owner, due date, remediation method, and escalation path for each item. If a patch is unavailable or unsafe, require an approved, time-bounded exception with compensating controls and a planned revisit date.
5. **Test proportionately.** Use representative staging or pilot systems, automated compatibility checks, backups, and rollback plans. Shorten the testing path for urgent, actively exploited flaws without skipping essential recovery safeguards.
6. **Deploy in controlled waves.** Automate repeatable deployment, prioritize reachable/high-risk assets, monitor service health, and keep an auditable record of successes, failures, and deferred devices.
7. **Verify, measure, and improve.** Confirm installed versions and rescan. Track remediation time by risk tier, percentage of assets within SLA, failed/offline deployment rates, overdue exceptions, unsupported assets, and recurrence. Use incidents and missed assets to improve inventory, tooling, and accountability.

## 6. Common challenges and how to overcome them

| Challenge | Why it delays patching | Practical response |
|---|---|---|
| **Incomplete asset inventory** | Teams may not know a vulnerable instance, dependency, appliance, or cloud image exists. | Reconcile endpoint, cloud, software-composition, and vulnerability-scanner inventories; require ownership and version metadata; monitor new and orphaned assets. |
| **Legacy or unsupported systems** | Vendors may no longer supply updates, or old applications may depend on fragile configurations. | Set a funded replacement date; isolate the system, restrict network paths, remove unnecessary services, apply vendor-supported mitigations, and monitor closely. Treat mitigations as temporary risk reduction, not equivalent to a security fix. |
| **Downtime and availability concerns** | Patches can require restarts or change behavior in critical services. | Use maintenance windows, redundancy/failover, canary rollout, service-owner coordination, and tested recovery. Prioritize exposed systems and define emergency windows for active exploitation. |
| **Testing and compatibility** | A patch may conflict with software, drivers, or integrations. | Maintain representative staging environments and automated regression tests; test high-impact combinations; use staged deployment and fast rollback. Bound test duration for urgent vulnerabilities. |
| **Competing priorities and unclear ownership** | Security, IT, application, and business teams may assume another team owns remediation. | Name an accountable asset owner and central patch process; set risk-based SLAs; provide executive escalation for overdue high-risk items. |
| **Remote or intermittently connected devices** | Devices may miss patch windows or remain powered off for weeks. | Use cloud-managed update services, compliance reporting, reconnect-triggered deployment, restricted access for noncompliant devices, and explicit follow-up for offline endpoints. |
| **Fear of breaking production** | A past failed update can encourage indefinite deferral. | Improve preproduction testing, backups, rollback, and staged release practices; compare the operational risk of patching with the documented risk of remaining exposed. |
| **Third-party dependencies and supply chain** | Applications may bundle vulnerable libraries that infrastructure scanning does not reveal. | Use software bills of materials where practical, dependency scanners, vendor attestations, and build pipelines that alert owners and block release of unapproved vulnerable versions. |

## 7. Conclusion

Patch management is a core preventive control, but it succeeds only when it is operationalized across people, processes, and technology. Accurate inventory answers “where are we exposed?” Risk-based prioritization answers “what must be fixed first?” Testing and staged rollout reduce change risk; verification demonstrates whether remediation actually reached the affected systems. The WannaCry and Equifax incidents show that a patch’s existence alone offers no protection: organizations need a measured process that gets fixes—or effective temporary mitigations—to the right assets before attackers do.

## References

1. National Institute of Standards and Technology (NIST), **SP 800-40 Rev. 4, *Guide to Enterprise Patch Management Planning: Preventive Maintenance for an Organization’s Technology***. https://csrc.nist.gov/pubs/sp/800/40/r4/final
2. CVE Program, **CVE Program Overview**. https://www.cve.org/About/Overview
3. NIST, **National Vulnerability Database (NVD)**. https://nvd.nist.gov/
4. Cybersecurity and Infrastructure Security Agency (CISA), **Known Exploited Vulnerabilities (KEV) Catalog**. https://www.cisa.gov/known-exploited-vulnerabilities-catalog
5. Forum of Incident Response and Security Teams (FIRST), **Common Vulnerability Scoring System v3.1 User Guide**. https://www.first.org/cvss/v3.1/user-guide
6. CISA, **Indicators Associated With WannaCry Ransomware**, Alert TA17-132A (12 May 2017). https://www.cisa.gov/news-events/alerts/2017/05/12/indicators-associated-wannacry-ransomware
7. Microsoft Security Response Center, **Customer Guidance for WannaCrypt Attacks** (May 2017). https://www.microsoft.com/en-us/msrc/blog/2017/05/customer-guidance-for-wannacrypt-attacks/
8. U.S. House Committee on Oversight and Government Reform, **The Equifax Data Breach** (2018). https://oversight.house.gov/wp-content/uploads/2018/12/Equifax-Report.pdf
9. U.S. Government Accountability Office (GAO), **Equifax Data Breach: Actions Taken by Equifax and Federal Agencies**, GAO-18-559 (2018). https://www.gao.gov/products/gao-18-559
10. Federal Trade Commission (FTC), **Equifax to Pay $575 Million as Part of Settlement Related to 2017 Data Breach** (22 July 2019). https://www.ftc.gov/news-events/news/press-releases/2019/07/equifax-pay-575-million-settlement-ftc-cfpb-states-related-2017-data-breach
11. IBM Security, **Cost of a Data Breach Report 2025**. https://www.ibm.com/reports/data-breach
