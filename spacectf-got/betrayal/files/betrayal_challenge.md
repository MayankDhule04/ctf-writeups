# Betrayal Challenge - Stolen Data Recovery

## Challenge Information
- **Scenario**: Employee stole confidential data, copied to external storage
- **Goal**: Find location of hidden hard disks
- **Clues**: 
  1. Encrypted token
  2. Website link
- **Flag Format**: `Kaal{...}`
- **Author**: Le0

## Encrypted Token
```
SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7
```

## Website
https://login-page-auqw.vercel.app/

## Analysis Notes
- Token looks like base64 or URL-safe base64
- Contains underscores and hyphens (URL-safe base64 indicators)
- Length: 204 characters
- Website is a login page on Vercel

## Next Steps
1. Visit the website
2. Analyze the login page
3. Try to decode the token
4. Look for clues about location
