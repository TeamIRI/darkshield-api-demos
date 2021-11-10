SET mypath=%~dp0
SET baseurl=localhost:8959
curl -X POST "http://%baseurl%/api/darkshield/searchContext.create" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"EmailMatcherContext\",\"matchers\":[{\"name\":\"EmailMatcher\",\"type\":\"pattern\",\"pattern\":\"\\b[\\w._%+-]+@[\\w.-]+\\.[\\w]{2,4}\\b\"}]}"
curl -X POST "http://%baseurl%/api/darkshield/files/fileSearchContext.create" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"EmailMatcherContext\",\"matchers\":[{\"name\":\"EmailMatcherContext\",\"type\":\"searchContext\"}]}"
curl -X POST "http://%baseurl%/api/darkshield/maskContext.create" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"HashEmailsContext\",\"rules\":[{\"name\":\"HashEmailRule\",\"type\":\"cosort\",\"expression\":\"hash_sha2(\\${EMAIL})\"}],\"ruleMatchers\":[{\"name\":\"HashEmailMatcher\",\"type\":\"name\",\"rule\":\"HashEmailRule\",\"pattern\":\"EmailMatcher\"}]}"
curl -X POST "http://%baseurl%/api/darkshield/files/fileMaskContext.create" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"HashEmailsContext\",\"rules\":[{\"name\":\"HashEmailsContext\",\"type\":\"maskContext\"}]}"
curl -X POST "http://%baseurl%/api/darkshield/files/fileSearchContext.mask" -H  "accept: multipart/form-data" -H  "Content-Type: multipart/form-data" -F "context={\"fileSearchContextName\": \"EmailMatcherContext\", \"fileMaskContextName\": \"HashEmailsContext\"}" -F "file=@%mypath%example.txt;type=text/plain"
curl -X POST "http://%baseurl%/api/darkshield/files/fileMaskContext.destroy" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"HashEmailsContext\"}"
curl -X POST "http://%baseurl%/api/darkshield/files/fileSearchContext.destroy" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"EmailMatcherContext\"}"
curl -X POST "http://%baseurl%/api/darkshield/maskContext.destroy" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"HashEmailsContext\"}"
curl -X POST "http://%baseurl%/api/darkshield/searchContext.destroy" -H  "accept: */*" -H  "Content-Type: application/json" -d "{\"name\":\"EmailMatcherContext\"}"
PAUSE
