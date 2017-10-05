#########
Changelog
#########

---
0.5
---
* raise warning instead of exception if expected image path is not available

---
0.4
---
* added footprint bounds to ``s2_inspect`` output
* added custom exception ``S2ReaderIOError`` if a file cannot be found
* added custom exception ``S2ReaderMetadataError`` if an unexpected metadata structure is detected
* fixed returned band paths & added flags for absolute or relative paths
