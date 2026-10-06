# Research Report: Common Network Security Threats

**Research report | 6 October 2026**

## Introduction

Networks connect users, applications, cloud services, and critical infrastructure, making them both essential and exposed. Attackers can abuse that connectivity to make services unavailable, impersonate systems, intercept communications, or redirect users to malicious destinations. A successful attack can interrupt business, expose credentials and sensitive data, enable follow-on compromise, and damage trust. Network administrators reduce these risks through layered controls: secure protocol configuration, resilient architecture, identity protection, monitoring, tested incident response, and coordination with service providers. No single control prevents every attack, and mitigation should be matched to the threat and the network’s risk profile.

## 1. Denial-of-Service and Distributed Denial-of-Service (DoS/DDoS)

### How the attack works

A denial-of-service attack attempts to make a service unavailable by exhausting a resource it needs, such as bandwidth, connection state, CPU, memory, or application capacity. In a **DoS**, the traffic may come from one system; in a **DDoS**, it comes from many systems, often compromised devices in a botnet. Attackers may also use reflection and amplification: they send small requests to exposed third-party services with the victim’s address forged as the source, causing larger replies to be sent to the victim. MITRE ATT&CK documents network DoS and notes the use of botnets and source-IP spoofing [1].

### Real-world example and impact

In February 2018, GitHub reported a memcached reflection/amplification DDoS attack that peaked at **1.35 Tbps** and **126.9 million packets per second**. GitHub’s report says the attack caused several minutes of unavailability and required shifting traffic to a provider with additional capacity and filtering [2]. The example shows that even a well-resourced online service can experience disruption; availability loss can interrupt customer access, business operations, and dependent services.

### Three specific mitigations

1. **Arrange upstream DDoS response before an incident.** Contract with an ISP, cloud provider, CDN, or specialized scrubbing service that can absorb and filter traffic upstream of the organization’s constrained links. Document the activation path and escalation contacts.
2. **Build for resilience.** Use redundant network paths and service instances, distribute traffic across regions where appropriate, cache static content, and avoid single points of failure. Capacity and autoscaling improve resilience but do not replace upstream filtering for attacks larger than the access link.
3. **Detect, triage, and apply targeted controls.** Baseline normal traffic, alert on abrupt volume/protocol shifts, and maintain a tested runbook. Apply provider-side filtering, rate limits, connection limits, or application-layer protections to the affected service while monitoring for impact on legitimate users.

## 2. Man-in-the-Middle (MITM) / Adversary-in-the-Middle

### How the attack works

In a man-in-the-middle (MITM), also called adversary-in-the-middle (AiTM), an attacker places themselves between communicating parties. They may observe, relay, or modify traffic. The position can be obtained through a rogue Wi-Fi access point, local network name-resolution spoofing, compromised DNS, a malicious proxy, or a routing compromise. If the communication is not properly authenticated and encrypted—or a user accepts an invalid certificate—the attacker may read or alter information. MITRE describes AiTM as positioning between networked devices and identifies traffic sniffing, manipulation, and replay as possible follow-on behavior [3].

### Real-world example and impact

In 2011, Mozilla reported that a fraudulent certificate for Google websites, issued through DigiNotar, had been used in the wild. Users on a compromised network could be redirected to sites presenting the fraudulent certificate and deceived into providing usernames and passwords [4]. The incident illustrates how a compromised certificate authority can undermine trust in encrypted web connections and enable credential theft or surveillance.

### Three specific mitigations

1. **Use authenticated encryption correctly.** Require current TLS for sensitive services, validate certificates and hostnames, and deploy HSTS for public websites. Never train users to bypass certificate warnings; investigate unexpected certificate errors.
2. **Secure local and remote network access.** Use WPA2/WPA3-Enterprise or an equivalent authenticated wireless configuration, disable automatic joining of unknown networks, and require an organization-managed VPN on untrusted networks when appropriate. A VPN does not protect against a compromised endpoint or a compromised VPN provider.
3. **Reduce the value of intercepted credentials and sessions.** Require phishing-resistant MFA for important accounts, use short-lived and protected session tokens, and monitor for unusual logins. MFA limits some credential-reuse consequences but does not prevent traffic interception itself.

## 3. IP Spoofing

### How the attack works

IP spoofing means forging the source address in an IP packet so that it appears to come from another system. It can obscure the sender’s true network location, impersonate a trusted address in weakly authenticated protocols, or direct replies toward a victim in a reflection attack. A forged address alone does not automatically let an off-path attacker complete a normal TCP connection, because the response is sent to the genuine address owner; spoofing is especially useful with connectionless protocols, reflection/amplification, or when the attacker can observe traffic on-path.

### Real-world example and impact

GitHub’s 2018 DDoS report describes how spoofed source addresses caused publicly reachable memcached servers to send amplified responses toward GitHub. The attack reached 1.35 Tbps [2]. Spoofing in this context contributed to a large availability attack; it can also complicate traffic attribution and incident investigation.

### Three specific mitigations

1. **Filter invalid source addresses at network boundaries.** Apply ingress filtering to reject packets arriving from customers or networks with source addresses that should not originate there, following the principles in IETF BCP 38 [5].
2. **Apply outbound filtering and routing checks.** Prevent internal hosts from sending packets with forged external source addresses. Use feasible-path or equivalent source validation (such as uRPF where topology permits) and review exceptions for multihomed networks, where strict checks can drop legitimate traffic.
3. **Avoid trust based only on source IP.** Authenticate sensitive protocols and administrative access cryptographically; use anti-replay protections where applicable. Combine this with rate limits and upstream DDoS protection, since address filtering cannot stop all spoofed traffic outside the administrator’s network.

## 4. DNS Poisoning and DNS Spoofing

### How the attack works

DNS translates names, such as `example.com`, into addresses and other records. **DNS cache poisoning** attempts to insert a false answer into a resolver’s cache; **DNS spoofing** broadly describes supplying a false DNS response or manipulating name resolution. Attackers may also compromise a domain registrar or authoritative DNS account and change legitimate records. These techniques are related but distinct: a forged resolver response is not the same mechanism as an unauthorized change to authoritative DNS.

If a victim accepts a false answer, they may be directed to an attacker-controlled site or mail server. The attacker can steal credentials, deliver malware, disrupt access, or intercept traffic. When control over a domain’s records enables the attacker to obtain a valid certificate for the redirected domain, ordinary browser certificate warnings may not appear.

### Real-world example and impact

CISA documented a global DNS infrastructure hijacking campaign in 2019. Attackers used compromised credentials to alter A, MX, or NS records, redirecting web and email traffic through attacker-controlled infrastructure. CISA noted that attackers could obtain valid encryption certificates for affected domains, enabling interception without the usual certificate warning [6]. This was DNS account/record hijacking rather than simply poisoning a recursive cache; it demonstrates the broader risk of DNS redirection.

### Three specific mitigations

1. **Protect control of DNS records.** Require phishing-resistant MFA where available for registrar and DNS-provider accounts, use unique credentials, restrict administrative roles, enable registrar/domain locks, and alert on record or nameserver changes.
2. **Deploy DNSSEC validation.** Sign authoritative zones and enable validation at recursive resolvers where operationally appropriate. DNSSEC can detect forged or altered DNS data when signatures are correctly deployed and validated; it does not prevent account compromise or an attacker from making changes through a legitimately authorized account.
3. **Monitor resolution and certificate changes.** Periodically compare public DNS records with approved values, alert on unexpected A/MX/NS changes, monitor certificate-transparency logs for unexpected certificates, and maintain a rehearsed process to revoke certificates and restore records.

## Comparison of threats

The difficulty and mitigation ratings below are qualitative and depend on attacker access, target configuration, scale, and available provider support. “Ease of mitigation” estimates how manageable the risk is with mature controls; it does not mean the attack can be completely prevented.

| Threat | Typical attack vector | Who is at risk | Difficulty to execute | Ease of mitigation |
|---|---|---|---|---|
| DoS/DDoS | Traffic flooding, botnets, or reflection/amplification against a public service | Public websites, APIs, DNS, gaming, hosting, and any service with limited capacity | Moderate; basic floods are accessible, but high-scale attacks require resources or abuse of amplifiers | Moderate; upstream scrubbing and resilient design help, but large attacks require provider coordination |
| MITM/AiTM | Rogue access point, local name-resolution spoofing, malicious proxy, compromised certificate or routing | Users on untrusted networks and services handling credentials or sensitive data | Moderate; easier on a shared/local network, harder against correctly authenticated end-to-end encryption | High for data confidentiality when modern authenticated encryption is correctly enforced; endpoint or trust-provider compromise remains a concern |
| IP spoofing | Forged packet source addresses; often UDP reflection or weak source-IP trust | Networks that accept forged traffic, spoofable services, and DDoS targets | Low to moderate for packet forgery; greater resources may be needed for effective attacks | Moderate; ingress/egress filtering reduces spoofing within managed networks, while the global Internet requires broad adoption |
| DNS poisoning/spoofing | Forged resolver answer, compromised resolver, or unauthorized authoritative DNS/registrar change | Domain owners, DNS resolvers, email users, and clients relying on affected names | Moderate; cache attacks may be technically demanding, while stolen DNS credentials can make record changes straightforward | Moderate to high with DNSSEC validation, strong account controls, monitoring, and response; no single measure covers every variant |

## Conclusion: three takeaways for a network administrator

1. **Protect availability upstream and plan before an outage.** DDoS resilience depends on provider coordination, monitoring, and tested response procedures—not only on a firewall or adding server capacity.
2. **Authenticate communications and network control planes.** Use correctly validated TLS, strong wireless and administrative authentication, DNS account protections, and cryptographic authentication rather than trusting an IP address or name-resolution response alone.
3. **Layer preventive, detective, and response controls.** Ingress filtering, DNSSEC, MFA, traffic monitoring, and change alerts reduce specific attack paths; a rehearsed incident plan helps contain attacks that still succeed. Regularly validate controls and account for the organization’s actual architecture.

## References

1. MITRE ATT&CK, **Network Denial of Service (T1498)**. https://attack.mitre.org/techniques/T1498/
2. GitHub Engineering, **DDoS Incident Report** (1 March 2018). https://github.blog/news-insights/company-news/ddos-incident-report/
3. MITRE ATT&CK, **Adversary-in-the-Middle (T1557)**. https://attack.mitre.org/techniques/T1557/
4. Mozilla Security Blog, **Fraudulent Google.com certificate** (29 August 2011). https://blog.mozilla.org/security/2011/08/29/fraudulent-google-com-certificate/
5. IETF, **RFC 2827: Network Ingress Filtering: Defeating Denial of Service Attacks which employ IP Source Address Spoofing**. https://www.rfc-editor.org/rfc/rfc2827
6. CISA, **DNS Infrastructure Hijacking Campaign**, Alert AA19-024A (24 January 2019; updated 13 February 2019). https://www.cisa.gov/news-events/cybersecurity-advisories/aa19-024a
7. IETF, **RFC 4033: DNS Security Introduction and Requirements**. https://www.rfc-editor.org/rfc/rfc4033
