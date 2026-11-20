# Equator Navigation System Challenge

## Challenge Information
- **Name**: Equator Navigation System
- **Description**: The Equator Navigation System monitors global coordinates. A secret transmission was encrypted and hidden within the system.
- **Goal**: Bypass security, solve the geohashing puzzle, and retrieve the flag
- **Flag Format**: `Kaal{...}`
- **Author**: M33T SH@H

## Key Terms
- **Equator Navigation System**: Suggests GPS/coordinate-based system
- **Global coordinates**: Latitude/Longitude
- **Geohashing**: A geocoding system that encodes geographic coordinates into short strings
- **Secret transmission**: Encrypted data
- **Bypass security**: May need to exploit vulnerabilities

## Geohashing Background
Geohashing is a method of encoding latitude and longitude into a short alphanumeric string. Common uses:
- Location-based services
- Spatial indexing
- Proximity searches

Common geohashing algorithms:
1. **Geohash** (standard): Encodes lat/lon into base32 string (e.g., "ezs42")
2. **H3** (Uber): Hexagonal hierarchical spatial index
3. **S2** (Google): Spherical geometry library
4. **Plus Codes** (Google): Open Location Code

## Next Steps
1. Get the challenge URL or files
2. Reconnaissance - explore the system
3. Identify the geohashing algorithm used
4. Find the encrypted transmission
5. Decode/decrypt to get flag

## Questions to Answer
- [ ] Is there a web interface?
- [ ] Are there any files provided?
- [ ] What endpoints are available?
- [ ] What geohashing algorithm is used?
- [ ] Where is the encrypted transmission?
- [ ] What encryption method is used?
