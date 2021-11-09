# DarkShield Files API: Text Search/Masking With Only Curl Posts

A batch file containing curl posts to the DarkShield-Files API. This is meant to be a simple demonstration of how to perform curl posts to the DarkShield-Files API.

The demonstration will search through a text file called example.txt and annotate any emails found using an email search context. Afterwards a hashing function will be performed on any emails that have been discovered.

The curl posts executed are:
  - Create a search context (/api/darkshield/searchContext.create)
  - Create a mask context (/api/darkshield/maskContext.create)
  - Create a file search context (/api/darkshield/files/fileSearchContext.create)
  - Create a file mask context (/api/darkshield/files/fileMaskContext.create)
  - Perform file search and mask operations (/api/darkshield/files/fileSearchContext.mask)
  - Destroy file mask context (/api/darkshield/files/fileMaskContext.destroy)
  - Destroy file search context (/api/darkshield/files/fileSearchContext.destroy)
  - Destroy mask context (/api/darkshield/maskContext.destroy)
  - Destroy search context (/api/darkshield/searchContext.destroy)
