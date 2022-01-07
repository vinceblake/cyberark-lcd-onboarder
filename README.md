# cyberark-lcd-onboarder
This is a simple automation. It retrieves a list of computers in a given EPM set and onboards them into the vault to a specific safe and platform. It is intended to allow for a simple import of LCD accounts from EPM into Privilege Cloud or self-hosted PAM. 

##Limitations / What This Does
This will add all LCD devices to the same safe and platform. It will **not** attempt to onboard accounts it finds within your defined safe but it will not check any other locations in the vault for the existence of those accounts. 

This is intended to onboard Windows built-in local Administrator accounts. It does not currently support Macs and it does not have any logic to differentiate a Mac from a Windows box. All machine names it finds in the set will be added indiscriminately as though they were Windows devices. Furthermore, this is untested with accounts other than built-in Administrator accounts (but may work just fine if you want to modify the code).

Finally, this assumes a dedicated set for LCD devices. There is no current endpoint for retrieving computers from a Credential Rotation policy, nor a way to differentiate computers in a given set that are being so managed from ones that are not. A better implementation of this might include setting up your Credential Rotation policy to manage a particular Group, then retrieving the computers in that group and onboarding only those. But that is not what this does.

##Notes
Although I have included support for ignoring SSL certificate verification by the requests module, you disable this at your own risk. Privilege Cloud customers will never need to do this.

The URL of your EPM API is visible in the address bar after you login to the SaaS portal. 

Most importantly, this does not represent any CyberArk-approved best practice and it is not officially supported in any way. It is provided as-is and, given its lack of exception handling, it should be used with caution. Be sure also to validate its results.

##How-To
1. Update all variables according to your environment, providing your own URLs and authentication information. I've used keyring to avoid hard-coding credentials and you should consider doing something similar. I might suggest Conjur (https://www.conjur.org/). 

2. Run onboarder.py to retrieve your EPM set IDs and define the epm_set_id variable accordingly.

3. Comment out lines 124-125 (now that you know your set ID) and uncomment lines 128 and 131.

4. Re-run onboarder.py.

5. Validate all results in the PVWA.

